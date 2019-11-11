from abc import ABCMeta, abstractmethod

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
