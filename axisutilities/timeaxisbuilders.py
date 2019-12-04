from __future__ import annotations

from abc import ABCMeta, ABC, abstractmethod
from calendar import monthrange
from datetime import datetime, date, timedelta
from typing import Iterable

import numpy as np

from axisutilities import Axis
from axisutilities.axisbuilder import AxisBuilder, FixedIntervalAxisBuilder, RollingWindowAxisBuilder
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class TimeAxisBuilder(AxisBuilder, ABC, metaclass=ABCMeta):
    """
    An abstract base class extending the `AxisBuilder` which is responsible to create `Axis` objects that are
    representing time.

    **Note:** Don't forget to call `.build()` at the end to get the actual `Axis` object.
    """

    def __init__(self, **kwargs):
        self.second_conversion_factor = kwargs.get("second_conversion_factor", SECONDS_TO_MICROSECONDS_FACTOR)

    @property
    def second_conversion_factor(self) -> int:
        return self._second_conversion_factor

    @second_conversion_factor.setter
    def second_conversion_factor(self, value):
        if value > 0:
            self._second_conversion_factor = value
        else:
            raise ValueError('a positive value must be provided.')

    @staticmethod
    def datetime_to_utc_timestamp(t: datetime, second_conversion=SECONDS_TO_MICROSECONDS_FACTOR) -> int:
        """
        Converts a datetime object to microseconds past January 1st, 1970. If the datetime object has time zone
        info, the time is adjusted to be UTC. However, if there are no time zone info available, it is assumed that
        the input is already in UTC.
        :param t: Must be a datetime object
        :param second_conversion: The default output would be in microseconds. You could provide a conversion factor
                                  to change the output unit. The conversion should be based on the second. For example,
                                  to get the result in miliseconds, provide 1000 or to get the result in minutes,
                                  provide (1 / 60) for this parameter.
        :return: Microseconds past January 1st, 1970.
        """
        if isinstance(t, datetime):
            base = datetime(1970, 1, 1, 0, 0, 0, 0, t.tzinfo)
            unadjusted = (t - base) // timedelta(seconds=1)
            adjustment = 0 if t.tzinfo is None else t.utcoffset().total_seconds()
            return int(round(
                (unadjusted - adjustment) * second_conversion
            ))
        else:
            raise TypeError("input must be of type datetime.")

    @staticmethod
    def date_to_utc_timestamp(t: date, second_conversion=SECONDS_TO_MICROSECONDS_FACTOR) -> int:
        if isinstance(t, date):
            return TimeAxisBuilder.datetime_to_utc_timestamp(
                datetime.fromisoformat(t.isoformat()),
                second_conversion
            )
        elif t is None:
            return None
        else:
            raise TypeError("input must be of type date.")

    @staticmethod
    def to_utc_timestamp(data_ticks: (datetime, date, str, Iterable), second_conversion=SECONDS_TO_MICROSECONDS_FACTOR, **kwrargs) -> (np.number, np.ndarray, None):
        if isinstance(data_ticks, datetime):
            return np.int64(TimeAxisBuilder.datetime_to_utc_timestamp(data_ticks, second_conversion))
        elif isinstance(data_ticks, date):
            return np.int64(TimeAxisBuilder.date_to_utc_timestamp(data_ticks, second_conversion))
        elif isinstance(data_ticks, str):
            raise NotImplemented("")
        elif data_ticks is None:
            return None
        elif isinstance(data_ticks, Iterable):
            return np.asarray(
                list(
                    map(lambda e: TimeAxisBuilder.to_utc_timestamp(e, second_conversion), data_ticks)
                ),
                dtype="int64"
            ).reshape((1, -1))
        else:
            raise TypeError("data_ticks must be either a single value of type date or datetime, "
                            "or and iterable where all of its elements are of type date or datetime.")

    @staticmethod
    def validate_date(input: date, name: str, none_is_ok: bool = True) -> (date, None):
        if isinstance(input, date):
            return input
        elif none_is_ok and (input is None):
            return None
        else:
            raise TypeError(f"{name} must be of type date")


class BaseCommonKnownIntervals(TimeAxisBuilder, metaclass=ABCMeta):
    @abstractmethod
    def get_dt(self) -> int:
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_date = TimeAxisBuilder.validate_date(kwargs.get("start_date", None), "start_date")
        self._end_date = TimeAxisBuilder.validate_date(kwargs.get("end_date", None), "end_date")
        self.set_n_interval(kwargs.get("n_interval", None))

    def set_start_date(self, start_date: date) -> BaseCommonKnownIntervals:
        self._start_date = TimeAxisBuilder.validate_date(start_date, "start_date")
        return self

    def set_end_date(self, end_date: date) -> BaseCommonKnownIntervals:
        self._end_date = TimeAxisBuilder.validate_date(end_date, "end_date")
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
            if (self._start_date is not None) and (self._end_date is not None):
                start = TimeAxisBuilder.to_utc_timestamp(self._start_date, self.second_conversion_factor)
                dt = self.get_dt()
                end = TimeAxisBuilder.to_utc_timestamp(self._end_date, self.second_conversion_factor)

                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._start_date is not None) and (self._n_interval is not None):
                start = TimeAxisBuilder.to_utc_timestamp(self._start_date, self.second_conversion_factor)
                dt = self.get_dt()
                end = start + self._n_interval * dt
                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()

            if (self._end_date is not None) and (self._n_interval is not None):
                end = TimeAxisBuilder.to_utc_timestamp(self._end_date, self.second_conversion_factor)
                dt = self.get_dt()
                start = end - self._n_interval * dt
                return FixedIntervalAxisBuilder(start=start, end=end, interval=dt).build()


class DailyTimeAxisBuilder(BaseCommonKnownIntervals):
    """
    As the name suggests, `DailyTimeAxisBuilder` creates a daily time axis.
    At minimum, you would need to provide two of the following configurations:

    - start_date: defining when the axis starts
    - end_date: defining when the axis ends
    - n_interval: defining how many intervals should there be in the axis, i.e. number of elements.

    **NOTE:** You could provide only two out of the three parameters above. Not more; even if they are consistent.

    Examples:
        * Create a Daily time axis for one week:

        >>> from axisutilities import DailyTimeAxisBuilder
        >>> from datetime import date
        >>> axis = DailyTimeAxisBuilder() \
        ...             .set_start_date(date(2019,1,1)) \
        ...             .set_end_date(date(2019,1,8)) \
        ...             .build()
        >>> axis.nelem
        7
        >>> axis.lower_bound
        array([[1546326000000000, 1546412400000000, 1546498800000000,
                1546585200000000, 1546671600000000, 1546758000000000,
                1546844400000000]])
        >>> axis.upper_bound
        array([[1546412400000000, 1546498800000000, 1546585200000000,
                1546671600000000, 1546758000000000, 1546844400000000,
                1546930800000000]])

        * Creating a Daily time axis for one week, but using a pattern more familiar in Python:

        >>> from axisutilities import DailyTimeAxisBuilder
        >>> from datetime import date
        >>> axis = DailyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     end_date=date(2019,1, 8)
        ... ).build()
        >>> axis.nelem
        7
        >>> axis.lower_bound
        array([[1546326000000000, 1546412400000000, 1546498800000000,
                1546585200000000, 1546671600000000, 1546758000000000,
                1546844400000000]])
        >>> axis.upper_bound
        array([[1546412400000000, 1546498800000000, 1546585200000000,
                1546671600000000, 1546758000000000, 1546844400000000,
                1546930800000000]])

        * Creating the same axis but using `n_interval`:

        >>> from axisutilities import DailyTimeAxisBuilder
        >>> from datetime import date
        >>> axis = DailyTimeAxisBuilder(
        ...     start_date=date(2019, 1, 1),
        ...     n_interval=7
        ... ).build()

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_dt(self) -> int:
        return int(round(
            timedelta(days=1).total_seconds() * self.second_conversion_factor
        ))


def DailyTimeAxis(**kwargs) -> Axis:
    return DailyTimeAxisBuilder(**kwargs).build()


class WeeklyTimeAxisBuilder(BaseCommonKnownIntervals):
    """
        As the name suggests, `WeeklyTimeAxisBuilder` creates a Weekly time axis, i.e. each element of the axis, covers
        one week. At minimum, you would need to provide two of the following configurations:

        - start_date: defining when the axis starts
        - end_date: defining when the axis ends
        - n_interval: defining how many intervals should there be in the axis, i.e. number of elements.

        **NOTE:** You could provide only two out of the three parameters above. Not more; even if they are consistent.

        Examples:
            * creating a two week span weekly time axis, i.e. two elements only:

            >>> axis = WeeklyTimeAxisBuilder(
            ...     start_date=date(2019,1,1),
            ...     end_date=date(2019,1,15)
            ... ).build()
            >>> axis.lower_bound
            array([[1546326000000000, 1546930800000000]])
            >>> axis.upper_bound
            array([[1546930800000000, 1547535600000000]])

            * Creating the same axis as above but differently:

            >>> axis = WeeklyTimeAxisBuilder(
            ...     start_date=date(2019,1,1),
            ...     n_interval=2
            ... ).build()
            >>> axis.lower_bound
            array([[1546326000000000, 1546930800000000]])
            >>> axis.upper_bound
            array([[1546930800000000, 1547535600000000]])
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_dt(self) -> int:
        return int(timedelta(days=7).total_seconds() * self.second_conversion_factor)


def WeeklyTimeAxis(**kwargs) -> Axis:
    return WeeklyTimeAxisBuilder(**kwargs).build()


class TimeAxisBuilderFromDataTicks(TimeAxisBuilder):
    """
    Creates a data axis from data ticks. You would need to provide extra information, i.e. `boundary_type` so
    that the object recognizes how to construct the upper and lower bounds.
    """
    _acceptable_boundary_types = {
        "centered"
    }

    def __init__(self, data_ticks=None, boundary_type="centered", **kwargs):
        super().__init__(**kwargs)
        if data_ticks is None:
            self._data_ticks = None
        else:
            self.set_data_ticks(data_ticks)

        self._boundary_type = "centered"
        self.set_boundary_type(boundary_type)

    def set_data_ticks(self, data_ticks: Iterable) -> TimeAxisBuilderFromDataTicks:
        self._data_ticks = TimeAxisBuilder.to_utc_timestamp(data_ticks, self.second_conversion_factor)
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
            boundary_type: str = "centered",
            **kwargs) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

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

    @staticmethod
    def from_xarray():
        # TODO
        raise NotImplemented("")


def TimeAxisFromDataTicks(**kwargs) -> Axis:
    return TimeAxisBuilderFromDataTicks(**kwargs).build()


class RollingWindowTimeAxisBuilder(TimeAxisBuilder, RollingWindowAxisBuilder):
    """
    Creates a Rolling Window Time Axis. This is similar to `RollingWindowAxisBuilder` except that you
    could provide a `date` or `datetime` object for the start and end in addition what you where able to
    provide before; also, for the base you could provide a `deltatime` object. Furthermore, `RollingWindowAxisBuilder`
    did not have any default value for `base`; but `RollingWindowTimeAxisBuilder` has a default value of one day
    for the `base` which is stored as microsecond.

    **NOTE:** if a `date` or a `datetime` object is provided for, `start_date`, and `end_date` or if a `deltatime`
    object is provided for the `base`, they are all converted to microseconds. So make sure if you are mixing these
    with other numbers, you do have a consistent number or unit. For example, if you are providing the start_date
    but then providing the `base` manually as an integer number, make sure that the `base` is in microsecond.
    """
    def __init__(self, **kwargs):
        TimeAxisBuilder.__init__(self, **kwargs)
        RollingWindowAxisBuilder.__init__(self, **kwargs)
        self.set_start_date(kwargs.get("start_date", None))
        self.set_end_date(kwargs.get("end_date", None))
        self.set_base(kwargs.get("base", int(timedelta(days=1).total_seconds()) * self.second_conversion_factor))

    def set_start_date(self, start_date: date) -> RollingWindowTimeAxisBuilder:
        self._start = TimeAxisBuilder.to_utc_timestamp(start_date, self.second_conversion_factor)
        return self

    def set_end_date(self, end_date: date) -> RollingWindowTimeAxisBuilder:
        self._end = TimeAxisBuilder.to_utc_timestamp(end_date, self.second_conversion_factor)
        return self

    def set_base(self, base: (int, timedelta)):
        if isinstance(base, timedelta):
            self._base = timedelta.total_seconds() * self.second_conversion_factor
        else:
            try:
                super().set_base(base)
            except TypeError:
                raise TypeError("base must be of type timedelta, a positive integer number, or "
                                "of an integral type that is positive.")

        return self


def RollingWindowTimeAxis(**kwargs) -> Axis:
    return RollingWindowTimeAxisBuilder(**kwargs).build()


class MonthlyTimeAxisBuilder(TimeAxisBuilder):
    """
    Creates a monthly time axis. You could define the  start/end Year/Month and it creates a time axis with
    monthly resolution.

    The start/end month are optional value. If you don't provide it, the start month is assumed to be January
    and the end month is assumed to be December.

    Examples:
        * Creating a 12 month long time axis covering 2019:

        >>> ta = MonthlyTimeAxisBuilder(
        ...             start_year=2019,
        ...             end_year=2019
        ...         ).build()

        * Creating 10 years long monthly time axis covering from January 2010 to December 2019:

        >>> ta = MonthlyTimeAxisBuilder(
        ...             start_year=2010,
        ...             end_year=2019
        ...         ).build()

        * Creating a time axis that covers September 2019 to end of March 2020:

        >>> ta = MonthlyTimeAxisBuilder(
        ...             start_year=2019,
        ...             start_month=9,
        ...             end_year=2020,
        ...             end_month=3
        ...         ).build()

    """
    def __init__(self, start_year: int, end_year: int, start_month: int = 1, end_month: int = 12, **kwargs):
        super().__init__(**kwargs)
        if (start_year is not None) and (start_month is not None):
            self.set_start_year_month(start_year, start_month)
        else:
            self._start = None

        if (end_year is not None) and (end_month is not None):
            self.set_end_year_month(end_year, end_month)
        else:
            self._end = None

    def set_start_year_month(self, start_year: int, start_month: int = 1) -> MonthlyTimeAxisBuilder:
        self._start = date(start_year, start_month, 1)
        return self

    def set_end_year_month(self, end_year: int, end_month: int = 12) -> MonthlyTimeAxisBuilder:
        self._end = date(end_year, end_month, monthrange(end_year, end_month)[1])
        return self

    def prebuild_check(self) -> (bool, Exception):
        if (self._start is None) or (self._end is None):
            raise ValueError("start and/or end year/month is not provided")

        if self._end < self._start:
            raise ValueError("start year/month must be before end year/month")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            start = self._start.year * 12 + (self._start.month - 1)
            end = self._end.year * 12 + (self._end.month - 1) + 1

            lower_bound = TimeAxisBuilder.to_utc_timestamp(
                [date(v // 12, (v % 12) + 1, 1) for v in range(start, end)],
                self.second_conversion_factor
            ).reshape((-1, ))

            upper_bound = TimeAxisBuilder.to_utc_timestamp(
                [date(v // 12, (v % 12) + 1, 1) for v in range(start + 1, end + 1)],
                self.second_conversion_factor
            ).reshape((-1,))

            data_ticks = 0.5 * (lower_bound + upper_bound)

            return Axis(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                data_ticks=data_ticks
            )


def MonthlyTimeAxis(**kwargs) -> Axis:
    return MonthlyTimeAxisBuilder(**kwargs).build()



