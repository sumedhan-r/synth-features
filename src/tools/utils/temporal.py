from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Self, TypeAlias

Numeric: TypeAlias = int | float | Decimal | Fraction
Hertz: TypeAlias = int | float


@dataclass(
    frozen=True
)  # frozen=True makes the class object immutable, easier for creating stable arguments
class Time:
    seconds: Decimal

    @classmethod
    def from_milliseconds(cls, milliseconds: Numeric) -> Self:
        return cls(Decimal(str(float(milliseconds))) / 1000)

    def __init__(self, seconds: Numeric) -> None:
        match seconds:
            case int() | float():
                object.__setattr__(self, "seconds", Decimal(str(seconds)))
            case Decimal():
                object.__setattr__(self, "seconds", seconds)
            case Fraction():
                object.__setattr__(self, "seconds", Decimal(str(float(seconds))))
            case _:
                raise TypeError(f"unsupported type '{type(seconds).__name__}'")

    def __add__(self, seconds: Numeric | Self) -> Self:
        match seconds:
            case Time() as time:
                return self.__class__(self.seconds + time.seconds)
            case int() | Decimal():
                return self.__class__(self.seconds + seconds)
            case float():
                return self.__class__(self.seconds + Decimal(str(seconds)))
            case Fraction():
                return self.__class__(Fraction.from_decimal(self.seconds) + seconds)
            case _:
                raise TypeError(f"can't add '{type(seconds).__name__}'")

    def get_num_samples(self, sampling_rate: Hertz) -> int:
        return round(self.seconds * round(sampling_rate))


@dataclass
class Timeline:
    instant: Time = Time(seconds=0)

    def __rshift__(self, seconds: Numeric | Time) -> Self:
        self.instant += seconds
        return self
