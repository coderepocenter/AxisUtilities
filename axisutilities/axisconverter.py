from __future__ import annotations

from typing import Iterable, Callable

import numpy as np
from numba import prange
from scipy.sparse import csr_matrix

from axisutilities import Axis


class AxisConverter:
    """
    `AxisConverter` facilitates conversion between two one-dimensional axis. Originally the idea started for performing
    various conversion between time axis. For example, let's say you have a hourly data and you want to average it to
    daily data. Or you have a daily data and you want to average it to weekly, monthly, or yearly data. Or may be you
    want to calculate daily minimum and maximum from an hourly data. However, since the same concept could be applied
    to any one-dimensional axis, the usage was generalized and the name was chaned to `AxisConverter`.

    `AxisConverter` caches bulk of the computations. Hence, once you create an object of the `AxisConverter` you could
    reuse it; hence, avoid re-doing certain computations, as long as the source/origin axis and the destination axis
    remain the same.

    `AxisConverter` applies the calculation on multi-dimensional data as well. By default, it assumes that the axis is
    the first dimension. If it is not the case, you could define the axis that that the conversion needs to happen.

    Currently it supports calculating `average`, `minimum`, `maximum`, or any user defined function (any Python
    Callable object).

    Examples:

        * Creating an `AxisConverter` and calculating average:

        >>> from axisutilities import AxisConverter
        >>> from axisutilities import DailyTimeAxisBuilder
        >>> from axisutilities import WeeklyTimeAxisBuilder
        >>> from datetime import date
        >>> daily_axis = DailyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     n_interval=14
        ... ).build()
        >>> weekly_axis = WeeklyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     n_interval=2
        ... ).build()
        >>> ac = AxisConverter(from_axis=daily_axis, to_axis=weekly_axis)
        >>> # Creating some random data
        ... import numpy as np
        >>> daily_data = np.random.random((14,1))
        >>> weekly_avg = ac.average(daily_data)
        >>> weekly_avg
        array([[0.71498815],
               [0.60443017]])
        >>> # creating a multidimensional data
        ... daily_data = np.random.random((14, 3, 4, 5))
        >>> weekly_avg = ac.average(daily_data)
        >>> weekly_avg.shape
        (2, 3, 4, 5)
        >>> # creating a multi-dimensional data with the axis being the last dimension
        ... daily_data = np.random.random((3, 4, 5, 14))
        >>> weekly_avg = ac.average(daily_data,dimension=3)
        >>> weekly_avg.shape
        (3, 4, 5, 2)
        >>> # Calculating min and max:
        ... weekly_min = ac.min(data)
        >>> weekly_min
        array([[0.19497718],
               [0.014242  ]])
        >>> weekly_max = ac.max(data)
        >>> weekly_max
        array([[0.99156943],
               [0.64039361]])


        * Applying a user-defined function:

        >>> from axisutilities import AxisConverter
        >>> from axisutilities import DailyTimeAxisBuilder
        >>> from axisutilities import WeeklyTimeAxisBuilder
        >>> from datetime import date
        >>> import numpy as np
        >>>
        >>> daily_axis = DailyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     n_interval=14
        ... ).build()
        >>>
        >>> weekly_axis = WeeklyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     n_interval=2
        ... ).build()
        >>>
        >>> ac = AxisConverter(from_axis=daily_axis, to_axis=weekly_axis)
        >>>
        >>> def user_defined_function(data):
        ...     return np.nansum(data, axis=0) * 42
        ...
        >>> daily_data = np.random.random((3, 4, 5, 14))
        >>>
        >>> weekly_user_defined = ac.apply_function(daily_data, user_defined_function, dimension=3)

    """
    def __init__(self, **kwargs) -> None:
        if ("from_axis" in kwargs) and ("to_axis" in kwargs):
            from_ta = kwargs["from_axis"]
            to_ta = kwargs["to_axis"]
            if not (isinstance(from_ta, Axis) and isinstance(to_ta, Axis)):
                raise TypeError("provided from/to_axis must be of type TimeAxis.")

            self._m = to_ta.nelem
            self._n = from_ta.nelem
            self._weight_matrix = self._get_coverage_csr_matrix(from_ta, to_ta)
            self._from_ta = from_ta
            self._to_ta = to_ta
        else:
            raise ValueError("Not enough information is provided to construct the TimeAxisConverter.")

    @property
    def from_nelem(self):
        return self._n

    @from_nelem.setter
    def from_nelem(self, v):
        pass

    @property
    def to_nelem(self):
        return self._m

    @to_nelem.setter
    def to_nelem(self, v):
        pass

    @property
    def weights(self) -> csr_matrix:
        return self._weight_matrix.copy()

    @weights.setter
    def weights(self, v):
        pass

    @property
    def from_axis(self):
        return self._from_ta

    @from_axis.setter
    def from_axis(self, v):
        pass

    @property
    def to_axis(self):
        return self._to_ta

    @to_axis.setter
    def to_axis(self, v):
        pass

    def _prep_input_data(self, in_data: Iterable, time_dimension) -> (np.ndarray, tuple):
        if not isinstance(in_data, Iterable):
            raise TypeError("input data should be an Iterable that can be casted to numpy.ndarray.")

        in_data_copy = in_data
        if not isinstance(in_data_copy, np.ndarray):
            in_data_copy = np.asarray(in_data_copy, dtype="float64")

        if in_data_copy.ndim == 1:
            in_data_copy = in_data_copy.reshape((-1, 1))

        n = self.from_nelem

        if in_data_copy.shape[time_dimension] != n:
            raise ValueError("The time dimension does not matches to that of the provided time converter.")

        if time_dimension != 0:
            in_data_copy = np.moveaxis(in_data_copy, time_dimension, 0)

        trailing_shape = in_data_copy.shape[1:]
        in_data_copy = in_data_copy.reshape((n, -1))

        return in_data_copy, trailing_shape

    @staticmethod
    def _prep_output_data( out_data: np.ndarray, time_dimension, trailing_shape: tuple):
        return np.moveaxis(out_data.reshape((out_data.shape[0], *trailing_shape)), 0, time_dimension)

    def average(self, from_data: Iterable, dimension=0) -> np.ndarray:
        from_data_copy, trailing_shape = self._prep_input_data(from_data, dimension)

        nan_mask = np.isnan(from_data_copy)
        non_nan_mask = np.ones(from_data_copy.shape, dtype=np.int8)
        non_nan_mask[nan_mask] = 0
        from_data_copy[nan_mask] = 0

        inverse_sum_effective_weights = np.reciprocal(self._weight_matrix * non_nan_mask)

        return self._prep_output_data(
            np.multiply(self._weight_matrix * from_data_copy, inverse_sum_effective_weights),
            dimension,
            trailing_shape
        )

    def apply_function(self, data: Iterable, func2apply: Callable, dimension=0):
        """
        Applies a user-defined/provided function for the conversion.

        :param data: The data on the source-axis that needs to be converted to the destination axis using the
                     user-provided function.
        :param func2apply: The user provided function. This function should assume that it will receives a `m` by `s`
                           matrix and it should return `1` by `s` output data. It should also handle the `NaN` or
                           missing values properly.
        :param dimension: The dimension where the source axis is. By default, it is assumed that the first dimension
                          is the source axis.
        :return: a data with the same number of dimension of the input, where each element is the result of the user
                 defined function. All the dimensions are the same as the input data except the source axis. The source
                 axis is turned into the destination axis; which means, it's location in the dimension is the same, but
                 it's size has changed to reflect that of the destination axis. For example, if you have 4 dimensional
                 input, and the source axis is the second dimension, the output would be still 4 dimensional and the
                 destination axis would be still the second dimension. But the second dimension between the input and
                 output might have different numbers depending on the axis.

        Examples:
            * Let's say we have a daily data, and we want to calculate coefficient of variation (CV) for each month.
              This is the proper way of defining the function:

            >>> from axisutilities import DailyTimeAxisBuilder
            >>> from axisutilities import MonthlyTimeAxisBuilder
            >>> from axisutilities import AxisConverter
            >>> from datetime import date
            >>>
            >>> # creating a daily axis with a span of one year
            ... daily_axis = DailyTimeAxisBuilder(
            ...     start_date=date(2019, 1, 1),
            ...     end_date=date(2020, 1, 1)
            ... ).build()
            >>>
            >>> # creating a monthly axis with a span of one year
            ... monthly_axis = MonthlyTimeAxisBuilder(
            ...     start_year=2019,
            ...     end_year=2019
            ... ).build()
            >>>
            >>> # constructing the AxisConverter object that conversts
            ... # from the daily axis to the monthly axis.
            ... ac = AxisConverter(from_axis=daily_axis, to_axis=monthly_axis)
            >>>
            >>> # creating some random data points
            ... from numpy.random import random
            >>> data = random((daily_axis.nelem, 90, 360))
            >>> print("data.shape: ", data.shape)
            data.shape:  (365, 90, 360)
            >>>
            >>> # now creating a function that calculates Coefficient of Variation (CV)
            ... import numpy as np
            >>> def cv(data):
            ...     return np.nanstd(data, axis=0) / np.nanmean(data, axis=0)
            ...
            >>> # now calculating the monthly CV
            ... monthly_cv = ac.apply_function(data, cv)
            >>> print("monthly_cv.shape: ", monthly_cv.shape)
            monthly_cv.shape:  (12, 90, 360)


            Note how cv function was provided.

            * Repeating the previous examples using lambda function: You do not need to have a named function to pass.
              You could create anonymous function using Lambda expressions:

            >>> monthly_cv_using_lambda = ac.apply_function(
            ...     data,
            ...     lambda e: np.nanstd(e, axis=0) / np.nanmean(e, axis=0)
            ... )
            >>> print("monthly_cv_using_lambda.shape: ", monthly_cv_using_lambda.shape)
            monthly_cv_using_lambda.shape:  (12, 90, 360)
            >>> np.min(monthly_cv_using_lambda - monthly_cv)
            0.0
            >>> np.max(monthly_cv_using_lambda - monthly_cv)
            0.0

        """
        data_copy, trailing_shape = self._prep_input_data(data, dimension)

        if isinstance(func2apply, Callable):
            import warnings
            warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
            output = _apply_function_core(
                self.to_nelem,
                self._weight_matrix,
                data_copy,
                func2apply.__call__
            )
        else:
            raise TypeError("func2apply must be a callable object that performs the calculation on axis=0.")

        return self._prep_output_data(
            output,
            dimension,
            trailing_shape
        )

    def min(self, data, dimension=0):
        return self.apply_function(
            data,
            lambda e: np.nanmin(e, axis=0),
            dimension
        )

    def max(self, data, dimension=0):
        return self.apply_function(
            data,
            lambda e: np.nanmax(e, axis=0),
            dimension
        )



    @staticmethod
    def _get_coverage_csr_matrix(from_ta: Axis, to_ta: Axis) -> csr_matrix:
        row_idx, col_idx, weights = AxisConverter._get_coverage(
            from_ta.lower_bound, from_ta.upper_bound,
            to_ta.lower_bound, to_ta.upper_bound
        )
        m = to_ta.nelem
        n = from_ta.nelem
        weights = csr_matrix((weights, (row_idx, col_idx)), shape=(m, n)).tolil()
        # with np.errstate(divide='ignore'):
        #     row_sum_reciprocal = np.reciprocal(np.asarray(weights.sum(axis=1)).flatten())
        # mask = np.isinf(row_sum_reciprocal)
        # row_sum_reciprocal[mask] = 0.0
        # inverse_row_sum = spdiags(row_sum_reciprocal, 0, m, m)
        #
        # normalized_weights = (inverse_row_sum * weights).tolil()
        # normalized_weights[mask, 0] = np.nan
        #
        # return normalized_weights.tocsr()

        mask = np.asarray(weights.sum(axis=1)).flatten() == 0
        weights[mask, 0] = np.nan
        return weights.tocsr()

    @staticmethod
    def _get_coverage(
            from_lower_bound: np.ndarray,
            from_upper_bound: np.ndarray,
            to_lower_bound: np.ndarray,
            to_upper_bound: np.ndarray):
        m = to_lower_bound.size
        n = from_lower_bound.size

        # basic sanity checks:
        if (to_lower_bound.ndim != 2) or (to_lower_bound.shape[0] != 1):
            raise ValueError(f"to_lower_bound must be of shape (1,m), it's current shape is: {to_lower_bound.shape}.")

        if to_lower_bound.shape != to_upper_bound.shape:
            raise ValueError("to_lower_bound/upper_bound must have the same shape.")

        if (from_lower_bound.ndim != 2) or (from_lower_bound.shape[0] != 1):
            raise ValueError("from_lower_bound must be of shape (1,n).")

        if from_lower_bound.shape != from_upper_bound.shape:
            raise ValueError("from_lower_bound/upper_bound must have the same shape.")

        # if np.any(from_lower_bound[0, :-1] > from_lower_bound[0, 1:]):
        #     raise ValueError("from_lower_bound must be monotonically increasing.")

        # TODO: turn this into cython so that is faster and/or use some sort of data structure to
        #       reduce its time-complexity from O(mn)
        # TODO: Move this to Interval; From OOP stand point it makes more sense to have some of these functionalities
        #       as part of that class/object.
        row_idx = []
        col_idx = []
        weights = []
        for r in range(m):
            toLB = to_lower_bound[0, r]
            toUB = to_upper_bound[0, r]
            for c in range(n):
                fromLB = from_lower_bound[0, c]
                fromUB = from_upper_bound[0, c]
                fromLength = fromUB - fromLB

                if (fromUB <= toLB) or (fromLB >= toUB):  # No coverage
                    continue
                elif (fromLB <= toLB) and (fromUB >= toLB) and (fromUB <= toUB):
                    row_idx.append(r)
                    col_idx.append(c)
                    weights.append((fromUB - toLB) / fromLength)
                elif (fromLB >= toLB) and (fromLB < toUB) and (fromUB >= toUB):
                    row_idx.append(r)
                    col_idx.append(c)
                    weights.append((toUB - fromLB) / fromLength)
                elif (fromLB >= toLB) and (fromUB <= toUB):
                    row_idx.append(r)
                    col_idx.append(c)
                    weights.append(1.0)
                elif (fromLB <= toLB) and (fromUB >= toUB):
                    row_idx.append(r)
                    col_idx.append(c)
                    weights.append((toUB - toLB) / fromLength)

        return row_idx, col_idx, weights


# @jit(parallel=True, forceobj=True, cache=True)
# @autojit
def _apply_function_core(n: int, _weight_matrix: csr_matrix, data_copy: np.ndarray, func: Callable) -> np.ndarray:
    output = np.full((n, data_copy.shape[1]), np.nan)
    for r in prange(n):
        start = _weight_matrix.indptr[r]
        end = _weight_matrix.indptr[r + 1]
        if not (np.isnan(_weight_matrix[r, 0]) and ((end - start) == 1)):
            row_mask = _weight_matrix.indices[start:end]
            output[r, :] = func(data_copy[row_mask, :])
    return output






















