from __future__ import annotations

from typing import Iterable, Callable

import numpy as np
from numba import prange
from scipy.sparse import csr_matrix

from axisutilities import Axis


class AxisConverter:
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

    def average(self, from_data: Iterable, time_dimension=0) -> np.ndarray:
        from_data_copy, trailing_shape = self._prep_input_data(from_data, time_dimension)

        nan_mask = np.isnan(from_data_copy)
        non_nan_mask = np.ones(from_data_copy.shape, dtype=np.int8)
        non_nan_mask[nan_mask] = 0
        from_data_copy[nan_mask] = 0

        inverse_sum_effective_weights = np.reciprocal(self._weight_matrix * non_nan_mask)

        return self._prep_output_data(
            np.multiply(self._weight_matrix * from_data_copy, inverse_sum_effective_weights),
            time_dimension,
            trailing_shape
        )

    def apply_function(self, data: Iterable, func2apply: Callable, time_dimension=0):
        data_copy, trailing_shape = self._prep_input_data(data, time_dimension)

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
            time_dimension,
            trailing_shape
        )

    def min(self, data, time_dimension=0):
        return self.apply_function(
            data,
            np.nanmin,
            time_dimension
        )

    def max(self, data, time_dimension=0):
        return self.apply_function(
            data,
            np.nanmax,
            time_dimension
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
            output[r, :] = func(data_copy[row_mask, :], axis=0)
    return output






















