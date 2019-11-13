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
        * Creating a 7-day daily axis:

        >>> axis = IntervalBaseAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             interval=24
        ...         ).build()

        * Creating a 7-day daily axis and binding the data ticks to 4 am every day:

        >>> axis = IntervalBaseAxisBuilder(
        ...             start=0,
        ...             end=7 * 24,
        ...             interval=24,
        ...             fraction=1.0/6.0
        ...         ).build()

        * Creating a 7-day daily axis and binding the first three days to the begining of the
          day, the 4th day to noon, and the last three days to the end of the day.

        >>> axis = IntervalBaseAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             interval=24,
        ...             fraction=[0, 0, 0, 0.5, 1, 1, 1]
        ...         ).build()

        * Creating an axis with different length/interval. In this example we create an axis that
          spans 7 days, but contains only three-element. The first element, covers 3 days, the second
          element convers one day, and the third element convers three days again:

        >>> axis = IntervalBaseAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             interval=[3*24, 24, 3*24]
        ...         ).build()
        >>> axis.lower_bound
        array([[ 0, 72, 96]])
        >>> axis.upper_bound
        array([[ 72,  96, 168]])

        * Passing the required inputs one by one: All these utilities follow the **Builder Design Pattern**
          and you are able to create them gradually.

        >>> axisBldr = IntervalBaseAxisBuilder()
        >>> # After doing some computation or file loading, you now know what the start date would be:
        ... axisBldr.set_start(start)
        >>> # Now based on the known start perhaps you need to do some more work
        ... # before you could decide what should be the end time. Once you have it:
        ... axisBldr.set_end(end)
        >>> # Now again based on the known start and end you could calculate the interval
        ... # it could be a single fixed interval, or a variable length interval:
        ... axisBldr.set_interval(interval)
        >>> # Now you are ready to build your axis
        ... axis = axisBldr.build()
        >>> # The default binding is middle. May be you decide to create two more axis
        ... # with the same configuration, i.e. start/end/interval, but different binding:
        ... axis_binding_to_beginning = axisBldr.set_fraction(0.0).build()
        >>> axis_binding_to_end = axisBldr.set_fraction(1.0).build()
        >>> axis_custom_binding = axisBldr.set_fraction(1.0/6.0).build()
        >>> # now you decide to create another axis with the same configuration but different
        ... # interval settings
        ... another_axis = axisBldr.set_interval(new_interval).build()
        >>> # Note that another_axis fraction is set to 1.0/6.0 (the last setting). If you want
        ... # to change that to the default binding you need to do one of the followings:
        ... another_axis = axisBldr.set_interval(0.5).set_interval(new_interval).build()
        >>> # or
        ... another_axis = axisBldr.set_interval(None).set_interval(new_interval).build()


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
    """
    This is essentially the same as `IntervalBaseAxisBuilder`; however, as the name suggest, you
    could only provide fixed interval. You cannot have varying length intervals. The following
    information could be provided.

    - start: defines the beginning of the axis
    - end: defines the end of the axis
    - interval: defines the interval or length for each element. Note that unlike `IntervalBaseAxisBuilder`, this
      can be only a scalar convertible to `int`
    - n_interval: defines how many interval do you want between the beginning and end.

    **NOTE:** You could only provide three out of the four item mentioned above; Even if you provide consistence input.

    for example you could provide `start`, `interval`, and `n_interval`, which the `end` is calculated accordingly. Or you could
    provide `end`, `interval`, `n_interval`, and the `start` is calculated.  Here are some examples

    Examples:
        * Creating 7 Day axis:

        >>> axis = FixedIntervalAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             n_interval=7
        ...         ).build()

        * The same as `IntervalBaseAxisBuilder`:

        >>> axis = FixedIntervalAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             interval=24
        ...         ).build()

        * Knowing the `end`, `interval`, and `n_interval`:

        >>> axis = FixedIntervalAxisBuilder(
        ...             end=7*24,
        ...             interval=24,
        ...             n_interval=7
        ...         ).build()

        * Knowing the `start`, `interval`, and `n_interval`:

        >>> axis = FixedIntervalAxisBuilder(
        ...             start=0,
        ...             interval=24,
        ...             n_interval=7
        ...         ).build()

    """
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
                self._end = self._start + self._n_interval * self._interval

            if self._mask == 14:
                # this means end, interval, and n_interval are provided
                self._start = self._end - self._n_interval * self._interval

            lower_bound = self._start + np.arange(self._n_interval, dtype="int64") * self._interval
            upper_bound = lower_bound + self._interval
            if upper_bound[-1] != self._end:
                raise ValueError(f"last element of upper_bound (i.e. {upper_bound[-1]}) is not the same "
                                 f"as provided end (i.e. {self._end}).")

            data_ticks = (1 - self._fraction) * lower_bound + self._fraction * upper_bound
            return Axis(lower_bound, upper_bound, data_ticks=data_ticks)


class RollingWindowAxisBuilder(AxisBuilder):
    """
    As the name suggests, creates an axis whose elements are overlapping. Combined with averaging operation,
    it becomes the same as moving average (or moving minimum, ...). The following information are needed:

    - start: when the axis starts
    - end: when the axis is ending.
    - base: the base unit of the axis.
    - window_size: the size of the window expressed as a positive odd integer relative to the base that
      is provided. For example, let's say base is set to be 24 (one day contains 24 hours) and then you set
      the window_size to 3; This means the window_size is 3 days (3 times the base).
    - n_window: number of window that you want to have.

    **NOTE:** you could provide either `end` or the `n_window`; but not both.
    **NOTE:** Again, don't forget to call `.build()` at the end.

    Note that each element is shifted one `base` forward. but each element of the axis covers the entire
    window_size. For example, if you set the `base` to be one day, the `window_size` to be 3 days, and the
    `start` to be hour 0, then the first element starts at 0 and ends at 72 hours (3 days). The second element
    starts at 24 (shifted one base (=one day in this example) forward) and ends at 96 hours.

    Examples:
        * Creating a rolling window by defining `start`, `end`, `base`, and `window_size`:

        >>> from axisutilities import RollingWindowAxisBuilder
        >>> axis = RollingWindowAxisBuilder(
        ...             start=0,
        ...             end=7*24,
        ...             base=24,
        ...             window_size=3
        ...         ).build()
        >>> axis.lower_bound
        array([[ 0, 24, 48, 72, 96]])
        >>> axis.upper_bound
        array([[ 72,  96, 120, 144, 168]])
        >>> axis.nelem
        5

        * Creating a rolling window by deifning `start`, `base`, `window_size`, and `n_window`:

        >>> axis = RollingWindowAxisBuilder(
        ...             start=0,
        ...             base=24,
        ...             window_size=3,
        ...             n_window=5
        ...         ).build()
        >>> axis.lower_bound
        array([[ 0, 24, 48, 72, 96]])
        >>> axis.upper_bound
        array([[ 72,  96, 120, 144, 168]])
        >>> axis.nelem
        5

    """
    def __init__(self, **kwargs):
        self.set_start(kwargs.get("start", None))
        self.set_end(kwargs.get("end", None))
        self.set_n_window(kwargs.get("n_window", None))
        self.set_window_size(kwargs.get("window_size", None))
        self.set_base(kwargs.get("base", None))

    def set_start(self, start: int) -> RollingWindowAxisBuilder:
        if (start is None) or isinstance(start, int):
            self._start = start
        else:
            try:
                self._start = int(start)
            except ValueError:
                raise TypeError("start_date must be None or an integral type.")

        return self

    def set_end(self, end: int) -> RollingWindowAxisBuilder:
        if (end is None) or isinstance(end, int):
            self._end = end
        else:
            try:
                self._end = int(end)
            except ValueError:
                raise TypeError("end_date must be None or an integral type.")
        return self

    def set_n_window(self, n_window: int) -> RollingWindowAxisBuilder:
        if isinstance(n_window, int):
            if n_window > 0:
                self._n_window = n_window
            else:
                raise ValueError("n_window must be a non-zero and positive integer.")
        elif n_window is None:
            self._n_window = None
        else:
            try:
                self.set_n_window(int(n_window))
            except ValueError:
                raise TypeError("n_window must be None or an integral type.")

        return self

    def set_window_size(self, window_size: int):
        if isinstance(window_size, int):
            if (window_size > 0) and (window_size % 2 == 1):
                self._window_size = window_size
            else:
                raise ValueError("window_size must be an odd positive number.")
        elif window_size is None:
            self._window_size = None
        else:
            try:
                self.set_window_size(int(window_size))
            except ValueError:
                raise TypeError("window_size must be None or an integral type.")

        return self

    def set_base(self, base: int):
        if isinstance(base, int):
            if base >= 1:
                self._base = base
            else:
                raise ValueError("base must be a positive integer.")
        elif base is None:
            self._base = None
        else:
            try:
                self.set_base(int(base))
            except TypeError:
                raise TypeError("base must be None or an integral type")

        return self

    def prebuild_check(self) -> (bool, Exception):
        if self._start is None:
            raise ValueError("start value is not provided.")

        if self._base is None:
            raise ValueError("base_dt is not provided")

        if self._window_size is None:
            raise ValueError("window size is not provided. window_size must a positive odd integer.")

        if (self._n_window is not None) and (self._end is not None):
            raise ValueError("You could provide either the end or the n_window; but not both.")

        if (self._n_window is None) and (self._end is None):
            raise ValueError("Neither end nor the n_window is provided. "
                             "You must provide exactly one of them.")

        if (self._start is not None) and (self._end is not None) and (self._start > self._end):
            raise ValueError("start must be before end.")

        return True

    def build(self) -> Axis:
        if self.prebuild_check():
            if self._end is not None:
                self._n_window = np.ceil((self._end - self._start) / self._base) - (self._window_size - 1)
            if self._n_window < 1:
                raise ValueError("the provided end_date and start_date resulted in 0 n_window.")

            lower_bound = self._start + \
                          np.arange(self._n_window, dtype="int64") * self._base

            window_length = self._window_size * self._base
            upper_bound = lower_bound + window_length
            data_tick = 0.5 * (lower_bound + upper_bound)
            return Axis(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                data_ticks=data_tick
            )

