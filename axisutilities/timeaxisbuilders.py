from __future__ import annotations
from abc import ABCMeta, ABC, abstractmethod
from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Iterable

import numpy as np

from axisutilities import Axis
from axisutilities.axisbuilder import AxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TimeAxisBuilder(AxisBuilder, ABC, metaclass=ABCMeta):
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


class IntervalBaseTimeAxisBuilder(TimeAxisBuilder):
    _key_properties = ['_start', '_end', '_interval']

    def __init__(self, **kwargs):
        self.set_start(kwargs.get("start", None))
        self.set_end(kwargs.get("end", None))
        self.set_interval(kwargs.get("interval", None))
        self.set_fraction(kwargs.get("fraction", 0.5))

    def set_start(self, start: int) -> FixedIntervalTimeAxisBuilder:
        if (start is None) or isinstance(start, int):
            self._start = start
        else:
            raise TypeError("start must be an int or None.")

        return self

    def set_end(self, end: int) -> FixedIntervalTimeAxisBuilder:
        if (end is None) or isinstance(end, int):
            self._end = end
        else:
            raise TypeError("end must be an int or None.")

        return self

    def set_interval(self, interval: [int, Iterable]) -> FixedIntervalTimeAxisBuilder:
        if isinstance(interval, int):
            self._interval = interval
        if isinstance(interval, Iterable):
            self._interval = np.asarray(list(interval), dtype=np.int64).reshape((1, -1))
        elif interval is None:
            self._interval = None
        else:
            raise TypeError("interval must be an int, an Iterable, or None.")

        return self

    def set_fraction(self, fraction: float) -> FixedIntervalTimeAxisBuilder:
        if isinstance(fraction, float):
            self._fraction = fraction
        elif fraction is None:
            self._fraction = 0.5
        else:
            raise TypeError("start must be a float or None.")

        if (self._fraction < 0) or (self._fraction > 1):
            raise ValueError("Fraction must be between 0 and 1.")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if (self._start is None) or (self._end is None) or (self._interval is None):
            raise ValueError("Not yet Ready to build the time axis.")

        if self._start > self._end:
            raise ValueError("Start must be smaller than  end")

        if (self._fraction is None) or (self._fraction < 0) or (self._fraction > 1):
            raise ValueError("some how fraction ended up to be None or out of bounds. "
                             f"Current Fraction Value: {self._fraction}")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            if isinstance(self._interval, int):
                lower_bound = np.arange(self._start, self._end, self._interval)
                upper_bound = np.arange(self._start + self._interval, self._end + 1, self._interval, dtype="int64")
            elif isinstance(self._interval, np.ndarray):
                interval_cumsum = np.concatenate(
                    (np.zeros((1, 1)),self._interval.cumsum().reshape((1, -1))),
                    axis=1
                ).astype(dtype="int64")
                lower_bound = self._start + interval_cumsum[0,:-1]
                upper_bound = self._start + interval_cumsum[0,1:]
            else:
                raise TypeError("Somehow interval ended up to be of a type other than an int or numpy.ndarray "
                                "(Iterable)")

            data_ticks = (1 - self._fraction) * lower_bound + self._fraction * upper_bound
            return Axis(lower_bound, upper_bound, data_ticks=data_ticks)


class FixedIntervalTimeAxisBuilder(IntervalBaseTimeAxisBuilder):
    _key_properties = ['_start', '_end', '_interval', '_n_interval']

    def __init__(self, **kwargs):
        self.set_n_interval(kwargs.get("n_interval", None))
        super().__init__(**kwargs)

    def set_interval(self, interval: int) -> FixedIntervalTimeAxisBuilder:
        if isinstance(interval, int):
            self._interval = interval
        elif interval is None:
            self._interval = None
        else:
            raise TypeError("interval must be an int or None.")

        return self

    def set_n_interval(self, n_interval: int) -> FixedIntervalTimeAxisBuilder:
        if isinstance(n_interval, int):
            self._n_interval = n_interval
        elif n_interval is None:
            self._n_interval = None
        else:
            raise TypeError("n_interval must be an int or None.")

        return self

    def prebuild_check(self) -> (bool, Exception):
        self._mask = 0
        self._n_available_keys = 0
        for idx in range(len(self._key_properties)):
            self._mask += 2 ** idx if self.__getattribute__(self._key_properties[idx]) is not None else 0
            self._n_available_keys += 1 if self.__getattribute__(self._key_properties[idx]) is not None else 0

        if self._n_available_keys != 3:
            raise ValueError(f"Only three out of the four {self._key_properties} "
                             f"could/should be provided. "
                             f"Currently {self._n_available_keys} are provided.")

        if self._mask not in {7, 11, 13, 14}:
            raise ValueError("wrong combination of inputs are provided.")

        if (self._start is not None) and (self._end is not None) and (self._start >= self._end):
            raise ValueError("start must be less than end.")

        if (self._interval is not None) and (self._interval<= 0.0):
            raise ValueError("interval must be a positive number.")

        if (self._n_interval is not None) and (self._n_interval < 1):
            raise ValueError("n_interval must be larger than 1.")

        if (self._fraction is None) or (self._fraction < 0) or (self._fraction > 1):
            raise ValueError("some how fraction ended up to be None or out of bounds. "
                             f"Current Fraction Value: {self._fraction}")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            if self._mask == 7:
                # this means start, end, and interval are provided
                self._n_interval = int((self._end - self._start)/self._interval)

                if self._n_interval < 1:
                    raise ValueError("provided input leaded to wrong n_interval.")

                if (self._start + self._n_interval * self._interval) != self._end:
                    raise ValueError("provided interval does not divide the start to end interval properly.")
            if self._mask == 11:
                # this means start, end, and n_interval are provided
                self._interval = int((self._end - self._start)/self._n_interval)

            if self._mask == 13:
                # this means start, interval, and n_interval are provided
                self._end = self._start + (self._n_interval + 1) * self._interval

            if self._mask == 14:
                # this means end, interval, and n_interval are provided
                self._start = self._end - (self._n_interval + 1) * self._interval

            lower_bound = self._start + np.arange(self._n_interval, dtype="int64") * self._interval
            upper_bound = lower_bound + self._interval
            if upper_bound[-1] != self._end:
                raise ValueError(f"last element of upper_bound (i.e. {upper_bound[-1]}) is not the same "
                                 f"as provided end (i.e. {self._end}).")

            data_ticks = (1 - self._fraction) * lower_bound + self._fraction * upper_bound
            return Axis(lower_bound, upper_bound, data_ticks=data_ticks)


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
                return FixedIntervalTimeAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._start_date is not None) and (self._n_interval is not None):
                start = int(TimeAxisBuilder.datetime_to_timestamp(self._start_date))
                dt = self.get_dt()
                end = start + self._n_interval * dt
                return FixedIntervalTimeAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._end_date is not None) and (self._n_interval is not None):
                end = int(TimeAxisBuilder.datetime_to_timestamp(self._end_date))
                dt = self.get_dt()
                start = end - self._n_interval * dt
                return FixedIntervalTimeAxisBuilder(start=start, end=end, interval=dt).build()


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

