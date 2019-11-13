from __future__ import annotations
import json

from datetime import datetime
from typing import Iterable, Dict

import numpy as np

from axisutilities import AxisBinding
from axisutilities.constants import SECONDS_TO_MICROSECONDS_FACTOR


class Interval:
    def __init__(self, lower_bound: int, upper_bound: int, data_tick: int):
        if not isinstance(lower_bound, int) or \
           not isinstance(upper_bound, int) or \
           not isinstance(data_tick, int):
            raise TypeError("All inputs must be of type int.")

        if (lower_bound > upper_bound) or \
           (data_tick > upper_bound) or \
           (data_tick < lower_bound):
            raise ValueError("Invalid inputs. Check lower_/upper_bound and data_tick")

        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._data_tick = data_tick
        self._fraction = (data_tick - lower_bound) / (upper_bound - lower_bound)

        self._binding = AxisBinding.valueOf(self._fraction)

    def asDict(self):
        return {
            "lower_bound": str(Interval.timestamp_to_datetime(self._lower_bound)),
            "upper_bound": str(Interval.timestamp_to_datetime(self._upper_bound)),
            "data_tick": str(Interval.timestamp_to_datetime(self._data_tick)),
            "fraction": self._fraction,
            "binding": str(self._binding)
        }

    def asJson(self):
        return json.dumps(self.asDict())

    def __repr__(self):
        summary = ["<timeaxis.TimeInterval>\n"]
        output = self.asDict()
        for key, value in output.items():
            if key in {"binding", "fraction"}:
                v = f"  > {key}:\n\t{value}\n"
            else:
                v = f"  > {key}:\n\t[{value[0]} ... {value[-1]}]\n"
            summary.append(v)
        return "\n".join(summary)

    @staticmethod
    def timestamp_to_datetime(ts: int) -> datetime:
        return datetime.fromtimestamp(ts/SECONDS_TO_MICROSECONDS_FACTOR)

    @property
    def lower_bound(self) -> int:
        return self._lower_bound

    @lower_bound.setter
    def lower_bound(self, v):
        pass

    @property
    def upper_bound(self) -> int:
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, v):
        pass

    @property
    def data_tick(self) -> int:
        return self._data_tick

    @data_tick.setter
    def data_tick(self, v):
        pass


class Axis:
    """
    Defines a one dimensional axis. Each element of axis is defined by three components:

    - lower bound
    - upper bound
    - data_tick

    For example, you could have a daily axis. Each entry is referring to one day; hence, the lower bound would be
    mid-night of that day, let's say, `2019-11-01 00:00:00` and the upper bound would be the mid-night of the next day,
    or in this example: `2019-11-02 00:00:00`. The data tick defines where in the interval are you associating the
    value. In some calculations this data tick is needed.

    There are multiple way of creating an axis:

    - Using Axis Object directly, or
    - Using one of the builder functions that are provided. These builder functions provide an easier way to create
      some well-known axis.

    For example, to create a 7 day daily time axis, you could either calculate the upper bound and lower bound along
    with other information and pass it to `Axis` initializer, or you could use `DailyTimeAxisBuilder` class which
    essentially you pass start day and number of days (or end day) and it creates an `Axis` by assigning proper lower
    and upper bound.

    **Note**: Although many of the examples here are creating a time axis; you are not limited to only that. Essentially
    any one dimensional axis is accepted.

    Examples:
        * Creating an Axis by passing lower/upper bound and data tick:

        >>> from axisutilities import Axis
        >>> lower_bound = [i * 24 for i in range(7)]
        >>> lower_bound
        [0, 24, 48, 72, 96, 120, 144]
        >>> upper_bound = [lower_bound[i] + 24 for i in range(7)]
        >>> upper_bound
        [24, 48, 72, 96, 120, 144, 168]
        >>> # Note that data ticks are converted to int. Any number yo pass is converted to int. so, if your
        ... # lower/upper/data_tick has fraction, you must first convert them to int properly. Otherwise,
        ... # you are loosing the fraction and you may get unexpected results or behavior.
        >>> data_ticks = [int(0.5*(lower_bound[i] + upper_bound[i])) for i in range(7)]
        >>> data_ticks
        [12, 36, 60, 84, 108, 132, 156]
        >>> axis = Axis(lower_bound=lower_bound,
        ...             upper_bound=upper_bound,
        ...             data_ticks=data_ticks)

        * Creating axis by passing upper/lower bound and defining the fraction: The following example is essentially the
          same as before, except that instead of manually defining the data ticks to be in the middle of (between) upper
          and lower bound we pass the fraction as 0.5 and the data ticks are calculated accordingly.

        >>> from axisutilities import Axis
        >>> lower_bound = [i * 24 for i in range(7)]
        >>> upper_bound = [lower_bound[i] + 24 for i in range(7)]
        >>> axis = Axis(lower_bound=lower_bound,
        ...             upper_bound=upper_bound,
        ...             fraction=0.5)

        * Creating axis by passing upper/lower bound and defining the bindings: If the data ticks are at the beginning,
          end or in the middle of the interval, instead of passing fraction as 0, 1, or 0.5, the alternative approach is
          to pass the binding by name:

        >>> axis = Axis(lower_bound=lower_bound,
        ...             upper_bound=upper_bound,
        ...             binding="middle")

        or

        >>> axis = Axis(lower_bound=lower_bound,
        ...             upper_bound=upper_bound,
        ...             binding="end")

        * Creating axis using variable fraction: The fraction does not need to be the same for all data ticks and
          it can change from one data element to another.

        >>> from numpy.random import random
        >>> fraction = random(7)
        >>> axis = Axis(lower_bound=lower_bound,
        ...             upper_bound=upper_bound,
        ...             fraction=fraction)

        * creating axis using one of the builder functions: There are numerous builder function that you could harness
          to quickly build your axis object. For example, to create a daily time axis for one year, instead of calculating
          and providing the upper and lower bounds manually, you could do:

        >>> from datetime import date
        >>> from axisutilities import DailyTimeAxisBuilder
        >>> axis = DailyTimeAxisBuilder(
        ...     start_date=date(2019,1,1),
        ...     end_date=date(2020,1,1)).build()
        >>> axis.nelem
        365

        Don't forget to call the `.build()` when using one of these builder functions.

    """
    def __init__(self,  lower_bound: Iterable[float],
                        upper_bound: Iterable[float],
                        **kwargs):
        """
        Initializes a ``TimeAxis`` object given the ``lower_bound``, ``upper_bound``, and either ``fraction`` or
        ``data_ticks``.

        :param lower_bound: The lower bound time stamps as a ``long`` value (or something that could be casted to
                            ``long``). The units must be in microseconds. The ``lower_bound`` values must be
                            monotonically increasing.
        :param upper_bound: The upper bound time stamps as a ``long`` value (or something that could be casted to
                            ``long``). The units must be in microseconds. The ``upper_bound`` does NOT need to be
                            monotonically increasing; however, they should not be smaller than their counter-part
                            ``lower_bound``.
        :param kwargs: One of the following keys (just one, not more) must be provided:
            - ``fraction``:
            - ``data_ticks``:
            - ``binding``:
        """
        # making sure at there is only one of the "fraction", "data_ticks", or "binding" are provided.
        if sum(list(map(lambda e: 1 if e in kwargs else 0, ['fraction', 'data_ticks', 'binding']))) != 1:
            raise ValueError("You must provide exactly just one of the 'fraction', 'data_ticks', or 'binding'.")

        self._bounds = Axis._create_bounds(lower_bound, upper_bound)
        self._nelem = self._bounds.shape[1]

        if "fraction" in kwargs:
            self._fraction = np.asarray(kwargs["fraction"], dtype="float64").reshape((1, -1))
            Axis._fraction_sanity_check(self._fraction)
            if (self._fraction.size != 1) and (self._fraction.size != self._nelem):
                raise ValueError("Fraction must be either a single number, or as many as there "
                                 "upper/lower bound values.")

            self._data_ticks = Axis._calculate_data_ticks_fromFraction(
                self._bounds[0, :],
                self._bounds[1, :],
                self._fraction
            )
            self._binding = Axis._get_binding(self._fraction)

        if "data_ticks" in kwargs:
            self._data_ticks = np.asarray(kwargs["data_ticks"], dtype="int64").reshape((1, -1))
            Axis._data_ticks_sanity_check(self._data_ticks)
            if self._data_ticks.size != self._nelem:
                raise ValueError("Data Ticks must have as many elements as there are lower/upper bound values.")

            self._fraction = Axis._calculate_fraction_from_data_ticks(
                self._bounds[0, :],
                self._bounds[1, :],
                self._data_ticks
            )

            self._binding = Axis._get_binding(self._fraction)


        if "binding" in kwargs:
            self._binding = AxisBinding.valueOf(kwargs["binding"])
            if self._binding == AxisBinding.CUSTOM_FRACTION:
                raise ValueError("Can't guess the fraction for the Custom Fraction. Use the fraction option instead.")
            self._fraction = np.asarray(self._binding.fraction(), dtype="float64").reshape((1, -1))
            self._data_ticks = Axis._calculate_data_ticks_fromFraction(
                self._bounds[0, :],
                self._bounds[1, :],
                self._fraction
            )

        if self._binding in (AxisBinding.BEGINNING, AxisBinding.MIDDLE, AxisBinding.END):
            self._fraction = np.asarray([self._fraction[0][0]], dtype="float64").reshape((1, -1))

    def asDict(self) -> Dict:
        """
        returns the current axis object as a python dictionary.
        :return: a dictionary representing the current axis.

        examples:
            * Converting to Dictionary:

            >>> axis.asDict()
            {'nelem': 7, 'lower_bound': [0, 24, 48, 72, 96, 120, 144],
            'upper_bound': [24, 48, 72, 96, 120, 144, 168],
            'data_ticks': [12, 36, 60, 84, 108, 132, 156],
            'fraction': [0.5],
            'binding': 'middle'}
        """
        out = {
            "nelem": self.nelem,
            "lower_bound": self._bounds[0, :].tolist(),
            "upper_bound": self._bounds[1, :].tolist(),
            "data_ticks": self._data_ticks.tolist()[0],
            "fraction": self._fraction.tolist()[0],
            "binding": str(self._binding)
        }

        return out

    @staticmethod
    def fromDict(input: dict) -> Axis:
        if "upper_bound" in input:
            upper_bound = input["upper_bound"]
        else:
            raise ValueError("Could not find upper bound.")

        if "lower_bound" in input:
            lower_bound = input["lower_bound"]
        else:
            raise ValueError("Could not find lower bound.")

        if "data_ticks" in input:
            data_ticks = input["data_ticks"]
        else:
            raise ValueError("Could not find data ticks.")

        return Axis(lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    data_ticks=data_ticks)

    def asJson(self) -> str:
        """
        Converts the current axis object to a JSON formatted string.
        :return: a JSON formatted string representing the current axis.

        examples:
            >>> axis.asJson()
            '{"nelem": 7, '
             '"lower_bound": [0, 24, 48, 72, 96, 120, 144], '
             '"upper_bound": [24, 48, 72, 96, 120, 144, 168], '
             '"data_ticks": [12, 36, 60, 84, 108, 132, 156], '
             '"fraction": [0.5], '
             '"binding": "middle"}'
        """
        return json.dumps(self.asDict())

    @staticmethod
    def fromJson(jsonstr: str) -> Axis:
        """
        Create an `Axis` object from a JSON formatted string:

        :param jsonstr: A JSON formatted string which must contain `lower_bound`, `upper_bound`, and `data_ticks`.
        :return: An `Axis` object.

        example:
            * Creating an `Axis` object from a JSON formatted String:

            >>> from axisutilities import Axis
            >>> s = '{"nelem": 7, "lower_bound": [0, 24, 48, 72, 96, 120, 144], "upper_bound": [24, 48, 72, 96, 120, 144, 168], "data_ticks": [12, 36, 60, 84, 108, 132, 156], "fraction": [0.5], "binding": "middle"}'
            >>> axis = Axis.fromJson(s)
        """
        return Axis.fromDict(json.loads(jsonstr))

    def __repr__(self):
        summary = ["<timeaxis.TimeAxis>\n"]
        output = self.asDict()
        for key, value in output.items():
            if key in {"binding", "nelem"}:
                v = f"  > {key}:\n\t{value}"
            else:
                v = f"  > {key}:\n\t[{value[0]} ... {value[-1]}]"
            summary.append(v)
        return "\n".join(summary)

    def __getitem__(self, item: int) -> Interval:
        if isinstance(item, int):
            if (item >= self.nelem) or (item < -self.nelem):
                raise IndexError("Index Out of range")
            return Interval(
                int(self._bounds[0, item]),
                int(self._bounds[1, item]),
                int(self._data_ticks[0, item])
            )
        else:
            raise TypeError("item must be an integer")

    def adjust_binding_to(self, **kwargs) -> Axis:
        if len(kwargs) == 1:
            if "fraction" in kwargs:
                return Axis(lower_bound=self._bounds[0, :],
                            upper_bound=self._bounds[1, :],
                            fraction=kwargs["fraction"])

            if "binding" in kwargs:
                return Axis(lower_bound=self._bounds[0, :],
                            upper_bound=self._bounds[1, :],
                            binding=kwargs["binding"])
        else:
            raise ValueError("you could provide either `fraction` or `binding` but not both and nothig else")

    @property
    def nelem(self) -> int:
        return self._nelem

    @nelem.setter
    def nelem(self, v) -> None:
        pass

    @property
    def lower_bound(self) -> np.ndarray:
        return self._bounds[0, :].copy().reshape((1, -1))

    @lower_bound.setter
    def lower_bound(self, v) -> None:
        pass

    @property
    def upper_bound(self) -> np.ndarray:
        return self._bounds[1, :].copy().reshape((1, -1))

    @upper_bound.setter
    def upper_bound(self, v) -> None:
        pass

    @property
    def fraction(self) -> np.ndarray:
        return self._fraction.copy()

    @fraction.setter
    def fraction(self, v) -> None:
        pass

    @property
    def data_ticks(self) -> np.ndarray:
        return self._data_ticks.copy()

    @data_ticks.setter
    def data_ticks(self, v) -> None:
        pass

    @staticmethod
    def _bounds_sanity_check(bounds: np.ndarray) -> (bool, Exception):
        # Making sure lower_i <= upper_i
        if bounds.shape[1] > 1:
            if np.any(bounds[:, 0] > bounds[:, 1]):
                raise ValueError("all lower bounds must be smaller than their counter-part upper bounds")

            # making sure lower_i < lower_{i+1}
            if np.any(bounds[0, :-1] >= bounds[0, 1:]):
                raise ValueError('lower bound values must be monotonically increasing.')

        # All good
        return True

    @staticmethod
    def _create_bounds(lower_bound: Iterable[float], upper_bound: Iterable[float]) -> np.ndarray:
        _bounds = np.asarray([list(lower_bound), list(upper_bound)], dtype="int64")
        Axis._bounds_sanity_check(_bounds)
        return _bounds

    @staticmethod
    def _data_ticks_sanity_check(data_tick: np.ndarray) -> (bool, Exception):
        # making sure data_tick_i < data_tick_{i+1}
        if np.any(data_tick[0, :-1] >= data_tick[0, 1:]):
            raise ValueError("data_tick must be monotonically increasing.")

        return True

    @staticmethod
    def _calculate_data_ticks_fromFraction(
            lower_bound: np.ndarray,
            upper_bound: np.ndarray,
            f: np.ndarray) -> np.ndarray:

        if np.any(f < 0) or np.any(f > 1):
            raise ValueError("all values of fraction must be between 0 and 1")
        data_tick = ((1.0 - f) * lower_bound + f * upper_bound).astype(np.int64)
        Axis._data_ticks_sanity_check(data_tick)
        return data_tick

    @ staticmethod
    def _fraction_sanity_check(fraction: np.ndarray) -> (bool, Exception):
        if np.any(fraction < 0):
            raise ValueError("all the data ticks values must be between their lower/upper bound.")

        return True

    @staticmethod
    def _calculate_fraction_from_data_ticks(
            lower_bound: np.ndarray,
            upper_bound: np.ndarray,
            data_ticks: np.ndarray) -> np.ndarray:

        fraction = ((data_ticks - lower_bound) /
                    (upper_bound - lower_bound)).astype(np.float64)

        Axis._fraction_sanity_check(fraction)

        return fraction

    @staticmethod
    def _get_binding(fraction: np.ndarray) -> AxisBinding:
        if np.all(fraction == 0.0):
            return AxisBinding.BEGINNING
        elif np.all(fraction == 1.0):
            return AxisBinding.END
        elif np.all(fraction == 0.5):
            return AxisBinding.MIDDLE
        elif np.all(0.0 <= fraction) and np.all(fraction <= 1.0):
            return AxisBinding.CUSTOM_FRACTION
        else:
            raise ValueError("fraction must be a number between 0.0 and 1.0")






