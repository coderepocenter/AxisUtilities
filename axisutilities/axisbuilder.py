from abc import ABCMeta, abstractmethod

from axisutilities import Axis


class AxisBuilder(metaclass=ABCMeta):
    @abstractmethod
    def prebuild_check(self) -> (bool, Exception):
        pass

    @abstractmethod
    def build(self) -> Axis:
        pass
