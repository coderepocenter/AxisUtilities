from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Iterable

import numpy as np

from axisutilities import Axis


class AxisBuilder(metaclass=ABCMeta):
    """
    An abstract class basis of all Axis Builders.
    """
    @abstractmethod
    def prebuild_check(self) -> (bool, Exception):
        pass

    @abstractmethod
    def build(self) -> Axis:
        pass


class IntervalBaseAxisBuilder(AxisBuilder):
    """
    This is the basic class to create an interval base time axis:
    The user should provide the following values:

    - a start value: a scalar value which could be converted to `int` defining the beginning of the axis.
    - an end value: a scalar value which could be converted to `int` defining the end of the axis.
    - inter value or values: a scalar value which could be converted to int or an iterable containing only elements
    that could be converted to `np.int64`. The iterable could be used to create axis with various size interval.
    - [fraction]: an optional fraction value that defines the data binding. The default value is 0.5, i.e. in the
    middle of the interval.

    **NOTE:** don't forget to call the `.build()` function to get an actual `Axis` object.

    Examples:


    """
    _key_properties = ['_start', '_end', '_interval']

    def __init__(self, **kwargs):
        self.set_start(kwargs.get("start", None))
        self.set_end(kwargs.get("end", None))
        self.set_interval(kwargs.get("interval", None))
        self.set_fraction(kwargs.get("fraction", 0.5))

    def set_start(self, start: int) -> IntervalBaseAxisBuilder:
        if (start is None) or isinstance(start, int):
            self._start = start
        else:
            try:
                self._start = int(start)
            except TypeError:
                raise TypeError("start must be an int, None, or a scalar object that can be converted to an int.")

        return self

    def set_end(self, end: int) -> IntervalBaseAxisBuilder:
        if (end is None) or isinstance(end, int):
            self._end = end
        else:
            try:
                self._end = int(end)
            except TypeError:
                raise TypeError("end must be an int, None, or a scalar object that can be converted to an int.")

        return self

    def set_interval(self, interval: [int, Iterable]) -> IntervalBaseAxisBuilder:
        if isinstance(interval, int):
            self._interval = interval
        if isinstance(interval, Iterable):
            self._interval = np.asarray(list(interval), dtype=np.int64).reshape((1, -1))
        elif interval is None:
            self._interval = None
        else:
            try:
                self._interval = int(interval)
            except TypeError:
             raise TypeError("interval must be an int, an Iterable, None, "
                             "or a scalar object that can be converted to an int.")

        return self

    def set_fraction(self, fraction: (float, Iterable)) -> IntervalBaseAxisBuilder:
        if isinstance(fraction, float):
            self._fraction = np.float(fraction)
        if isinstance(fraction, Iterable):
            self._fraction = np.asarray(fraction, dtype="float").reshape((1, -1))
        elif fraction is None:
            self._fraction = 0.5
        else:
            try:
                self._fraction = np.float(fraction)
            except TypeError:
                raise TypeError("start must be a float, None, "
                                "or a scalar/iterable object that can be converted to a float.")

        if np.any(self._fraction < 0) or np.any(self._fraction > 1):
            raise ValueError("Fraction must be between 0 and 1.")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if (self._start is None) or (self._end is None) or (self._interval is None):
            raise ValueError("Not yet Ready to build the time axis.")

        if self._start > self._end:
            raise ValueError("Start must be smaller than  end")

        if (self._fraction is None) or np.any(self._fraction < 0) or np.any(self._fraction > 1):
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
                lower_bound = self._start + interval_cumsum[0, :-1]
                upper_bound = self._start + interval_cumsum[0, 1:]
            else:
                raise TypeError("Somehow interval ended up to be of a type other than an int or numpy.ndarray "
                                "(Iterable)")

            data_ticks = (1 - self._fraction) * lower_bound + self._fraction * upper_bound
            return Axis(lower_bound, upper_bound, data_ticks=data_ticks)


class FixedIntervalAxisBuilder(IntervalBaseAxisBuilder):
    _key_properties = ['_start', '_end', '_interval', '_n_interval']

    def __init__(self, **kwargs):
        self.set_n_interval(kwargs.get("n_interval", None))
        super().__init__(**kwargs)

    def set_interval(self, interval: int) -> FixedIntervalAxisBuilder:
        if isinstance(interval, int):
            self._interval = interval
        elif interval is None:
            self._interval = None
        else:
            raise TypeError("interval must be an int or None.")

        return self

    def set_n_interval(self, n_interval: int) -> FixedIntervalAxisBuilder:
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




