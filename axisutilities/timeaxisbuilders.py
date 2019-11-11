from __future__ import annotations
from abc import ABCMeta, ABC, abstractmethod
from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Iterable

import numpy as np

from axisutilities import Axis
from axisutilities.axisbuilder import AxisBuilder, FixedIntervalAxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TimeAxisBuilder(AxisBuilder, ABC, metaclass=ABCMeta):
    """
    An abstract base class extending the `AxisBuilder` which is responsible to create `Axis` objects that are
    representing time.

    **Note:** Don't forget to call `.build()` at the end to get the actual `Axis` object.
    """
    @staticmethod
    def datetime_to_timestamp(data_ticks: (datetime, date, str, Iterable), **kwrargs) -> np.ndarray:
        if isinstance(data_ticks, date):
            return np.asarray(
                [datetime.strptime(data_ticks.strftime("%c"), "%c").timestamp() * SECONDS_TO_MICROSECONDS_FACTOR],
                dtype="int64"
            )
        elif isinstance(data_ticks, datetime):
            return np.asarray(
                [data_ticks.timestamp() * SECONDS_TO_MICROSECONDS_FACTOR],
                dtype="int64"
            )
        elif isinstance(data_ticks, str):
            raise NotImplemented("")
        elif isinstance(data_ticks, Iterable):
            return np.asarray(
                list(
                    map(lambda e: TimeAxisBuilder.datetime_to_timestamp(e), data_ticks)
                ),
                dtype="int64"
            ).flatten().reshape((1, -1))
        else:
            raise TypeError("data_ticks must be either a single value of type date or datetime, "
                            "or and iterable where all of its elements are of type date or datetime.")


class BaseCommonKnownIntervals(TimeAxisBuilder, metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def get_dt() -> int:
        pass

    def __init__(self, **kwargs):
        self.set_start_date(kwargs.get("start_date", None))
        self.set_end_date(kwargs.get("end_date", None))
        self.set_n_interval(kwargs.get("n_interval", None))

    def set_start_date(self, start_date: date) -> BaseCommonKnownIntervals:
        if (start_date is None) or isinstance(start_date, date):
            self._start_date = start_date
        else:
            raise TypeError("start_date must be of type date.")

        return self

    def set_end_date(self, end_date: date) -> BaseCommonKnownIntervals:
        if (end_date is None) or isinstance(end_date, date):
            self._end_date = end_date
        else:
            raise TypeError("end_date must be of type date.")

        return self

    def set_n_interval(self, n_interval: int) -> BaseCommonKnownIntervals:
        self._n_interval = None if n_interval is None else int(n_interval)
        return self

    def prebuild_check(self) -> (bool, Exception):
        if sum(list(map(
                lambda e: 1 if self.__getattribute__(e) is not None else 0,
                ["_start_date", "_end_date", "_n_interval"]))) != 2:
            raise ValueError('Only two out of the "_start_date", "_end_date", or "_n_interval" could be provided.')

        if (self._start_date is not None) and \
           (self._end_date is not None) and \
           (self._start_date > self._end_date):
            raise ValueError("start_date cannot be larger than end_date.")

        if (self._n_interval is not None) and (self._n_interval < 1):
            raise ValueError("n_interval must be at least 1.")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            # # Older implementation
            # dt = np.int64(timedelta(days=1).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)
            # nDays = (self._end_date - self._start_date).days + 1
            # lower_bound = np.arange(nDays, dtype="int64") * dt + TimeAxisBuilder.datetime_to_timestamp(self._start_date)
            # upper_bound = lower_bound + dt
            # data_ticks = lower_bound + np.int64(timedelta(hours=12).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)

            # return TimeAxis(lower_bound, upper_bound, data_ticks=data_ticks)

            if (self._start_date is not None) and (self._end_date is not None):
                start = int(TimeAxisBuilder.datetime_to_timestamp(self._start_date))
                dt = self.get_dt()
                end = int(TimeAxisBuilder.datetime_to_timestamp(self._end_date))
                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._start_date is not None) and (self._n_interval is not None):
                start = int(TimeAxisBuilder.datetime_to_timestamp(self._start_date))
                dt = self.get_dt()
                end = start + self._n_interval * dt
                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._end_date is not None) and (self._n_interval is not None):
                end = int(TimeAxisBuilder.datetime_to_timestamp(self._end_date))
                dt = self.get_dt()
                start = end - self._n_interval * dt
                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()


class DailyTimeAxisBuilder(BaseCommonKnownIntervals):
    @staticmethod
    def get_dt() -> int:
        return int(timedelta(days=1).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)


class WeeklyTimeAxisBuilder(BaseCommonKnownIntervals):
    @staticmethod
    def get_dt() -> int:
        return int(timedelta(days=7).total_seconds() * SECONDS_TO_MICROSECONDS_FACTOR)


class TimeAxisBuilderFromDataTicks(TimeAxisBuilder):
    _acceptable_boundary_types = {
        "centered"
    }

    def __init__(self, data_ticks=None, boundary_type="centered", **kwargs):
        if data_ticks is None:
            self._data_ticks = None
        else:
            self.set_data_ticks(data_ticks)

        self._boundary_type = "centered"
        self.set_boundary_type(boundary_type)

    def set_data_ticks(self, data_ticks: Iterable) -> TimeAxisBuilderFromDataTicks:
        self._data_ticks = TimeAxisBuilder.datetime_to_timestamp(data_ticks)
        return self

    def set_boundary_type(self, boundary_type) -> TimeAxisBuilderFromDataTicks:
        if isinstance(boundary_type, str):
            boundary_type_lower = boundary_type.lower()
            if boundary_type_lower in self._acceptable_boundary_types:
                self._boundary_type = boundary_type_lower
            else:
                raise ValueError(f"Unrecognized boundary type. Currently acceptable values are: "
                                 f"[{', '.join(self._acceptable_boundary_types)}].")
        else:
            raise TypeError(f"boundary_type must be a string set to one of the "
                            f"following values: {str(self._acceptable_boundary_types)}")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if self._data_ticks is None:
            raise ValueError("data_ticks are not set yet.")

        if self._boundary_type is None:
            raise ValueError("Boundary Type is not provided.")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            lower_bound, data_tickes, upper_bound = TimeAxisBuilderFromDataTicks._calculate_bounds(
                data_ticks=self._data_ticks,
                boundary_type=self._boundary_type
            )

            return Axis(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                data_ticks=data_tickes
            )

    @staticmethod
    def _calculate_bounds(
            data_ticks: np.ndarray,
            boundary_type: str = "centered") -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        if not isinstance(data_ticks, np.ndarray):
            raise TypeError("This method only accepts numpy.ndarry.")

        if data_ticks.ndim == 1:
            data_ticks = data_ticks.reshape((-1, ))

        if (data_ticks.ndim == 2) and ((data_ticks.shape[0] != 1) or ((data_ticks.shape[1] != 1))):
            data_ticks = data_ticks.reshape((-1, ))

        if (data_ticks.ndim != 1):
            raise ValueError("data_ticks must be a row/column of numbers.")

        if data_ticks.dtype != 'int64':
            data_ticks = data_ticks.astype(np.int64)

        boundary_type = boundary_type.lower()
        if boundary_type == "centered":
            avg = (0.5 * (data_ticks[:-1] + data_ticks[1:])).astype(np.int64)

            n = data_ticks.size

            lower_boundary: np.ndarray = np.ndarray((n, ), dtype=np.int64)
            lower_boundary[0] = 2 * data_ticks[0] - avg[0]
            lower_boundary[1:] = avg

            upper_boundary: np.ndarray = np.ndarray((n, ), dtype=np.int64)
            upper_boundary[-1] = 2 * data_ticks[-1] - avg[-1]
            upper_boundary[:-1] = avg

            return lower_boundary, data_ticks, upper_boundary
        else:
            raise ValueError("Unrecognized boundary type.")


class RollingWindowTimeAxisBuilder(TimeAxisBuilder):
    def __init__(self, **kwargs):
        self.set_start_date(kwargs.get("start_date", None))
        self.set_end_date(kwargs.get("end_date", None))
        self.set_n_window(kwargs.get("n_window", None))
        self.set_window_size(kwargs.get("window_size", None))
        self.set_base_dt(kwargs.get("base_dt", int(timedelta(days=1).total_seconds()) * SECONDS_TO_MICROSECONDS_FACTOR))

    def set_start_date(self, start_date: date) -> RollingWindowTimeAxisBuilder:
        if (start_date is None) or isinstance(start_date, date):
            self._start_date = start_date
        else:
            raise TypeError("start_date must be of type date")

        return self

    def set_end_date(self, end_date: date) -> RollingWindowTimeAxisBuilder:
        if (end_date is None) or isinstance(end_date, date):
            self._end_date = end_date
        else:
            raise TypeError("end_date must be of type date")
        return self

    def set_n_window(self, n_window: int) -> RollingWindowTimeAxisBuilder:
        if isinstance(n_window, int):
            if n_window > 0:
                self._n_window = n_window
            else:
                raise ValueError("n_window must be a non-zero and positive integer.")
        elif n_window is None:
            self._n_window = None
        else:
            raise TypeError("n_window must be an int")

        return self

    def set_window_size(self, window_size: int):
        if isinstance(window_size, int):
            if (window_size > 0) or (window_size % 2 != 1):
                self._window_size = window_size
            else:
                raise ValueError("window_size must be an odd positive number.")
        elif window_size is None:
            self._window_size = None
        else:
            raise TypeError("window_size must be an int")

        return self

    def set_base_dt(self, base_dt: int):
        if isinstance(base_dt, int):
            if base_dt > 1:
                self._base_dt = base_dt
            else:
                raise ValueError("base_dt must be a positive integer.")
        elif base_dt is None:
            self._base_dt = None
        else:
            raise TypeError("base_dt must be an int")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if self._start_date is None:
            raise ValueError("start_date is not provided.")

        if self._base_dt is None:
            raise ValueError("Some how base_dt ended up to be None. It cannot be None")

        if self._window_size is None:
            raise ValueError("Window_size is not provided. window_size must a positive integer.")

        if (self._n_window is not None) and (self._end_date is not None):
            raise ValueError("You could provide either the end_date or the n_window; but not both.")

        if (self._n_window is None) and (self._end_date is None):
            raise ValueError("Neither end_date nor the n_window is provided. "
                             "You must provide exactly one of them.")

        if (self._start_date is not None) and (self._end_date is not None) and (self._start_date > self._end_date):
            raise ValueError("start_date must be before end_date.")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            if self._end_date is not None:
                self._n_window = np.ceil(
                    (TimeAxisBuilder.datetime_to_timestamp(self._end_date) -
                     TimeAxisBuilder.datetime_to_timestamp(self._start_date)) / self._base_dt
                ) - (self._window_size - 1)
                if self._n_window < 1:
                    raise ValueError("the provided end_date and start_date resulted in 0 n_window.")

            lower_bound = TimeAxisBuilder.datetime_to_timestamp(self._start_date) + \
                          np.arange(self._n_window, dtype="int64") * self._base_dt

            window_length = self._window_size * self._base_dt
            upper_bound = lower_bound + window_length
            data_tick = 0.5 * (lower_bound + upper_bound)
            return Axis(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                data_ticks=data_tick
            )


class MonthlyTimeAxisBuilder(TimeAxisBuilder):
    def __init__(self, start_year: int, end_year: int, start_month: int =1, end_month: int = 12):
        if (start_year is not None) and (start_month is not None):
            self.set_start_year_month(start_year, start_month)
        else:
            self._start = None

        if (end_year is not None) and (end_month is not None):
            self.set_end_year_month(end_year, end_month)
        else:
            self._end = None

    def set_start_year_month(self, start_year: int, start_month: int = 1) -> MonthlyTimeAxisBuilder:
        tmp_start_year = int(start_year)
        tmp_start_month = int(start_month)

        if 1<= start_month <= 12:
            self._start = date(tmp_start_year, tmp_start_month, 1)
        else:
            raise ValueError("start_year/month must be convertible to an integer value and "
                             "start_month must be a number between 1 and 12")

        return self

    def set_end_year_month(self, end_year: int, end_month: int = 12) -> MonthlyTimeAxisBuilder:
        tmp_end_year = int(end_year)
        tmp_end_month = int(end_month)

        if 1 <= end_month <= 12:
            self._end = date(tmp_end_year, tmp_end_month, monthrange(tmp_end_year, tmp_end_month)[1])
        else:
            raise ValueError("end_year/month must be convertible to an integer value and "
                             "end_month must be a number between 1 and 12")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if (self._start is None) or (self._end is None):
            raise ValueError("start and/or end year/month is not provided")

        if self._end < self._start:
            raise ValueError("start year/month must be before end year/month")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            n_month_in_first_year = 12 - self._start.month + 1
            n_month_in_last_year = self._end.month
            n_years_in_between = self._end.year - self._start.year - 1

            n_months = n_month_in_first_year + n_years_in_between * 12 + n_month_in_last_year

            year_list = np.concatenate((
                np.ones(n_month_in_first_year, dtype="int") * self._start.year,
                np.repeat(np.arange(n_years_in_between, dtype="int") + self._start.year + 1, 12),
                np.ones(n_month_in_last_year, dtype="int") * self._end.year
            ))
            month_list = (np.arange(n_months, dtype="int") + (self._start.month - 1)) % 12 + 1
            lower_bound = TimeAxisBuilder.datetime_to_timestamp(
                [date(y, m, 1) for y, m in zip(year_list, month_list)]
            ).reshape((-1, ))
            upper_bound = TimeAxisBuilder.datetime_to_timestamp(
                [date(y, m, monthrange(y, m)[1]) for y, m in zip(year_list, month_list)]
            ).reshape((-1, ))

            data_ticks = 0.5 * (lower_bound + upper_bound)

            return Axis(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                data_ticks=data_ticks
            )

