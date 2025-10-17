from dataclasses import dataclass, field
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

    def __add__(
        self, seconds: Numeric | Self
    ) -> Self:  # Only works for left operand : X = Time() * k
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

    def __mul__(
        self, seconds: Numeric
    ) -> Self:  # Only works for left operand : X = Time() * k
        match seconds:
            case int() | Decimal():
                return self.__class__(self.seconds * seconds)
            case float():
                return self.__class__(self.seconds * Decimal(str(seconds)))
            case Fraction():
                return self.__class__(Fraction.from_decimal(self.seconds) * seconds)
            case _:
                raise TypeError(f"can't multiply by '{type(seconds).__name__}'")

    def get_num_samples(self, sampling_rate: Hertz) -> int:
        return round(self.seconds * round(sampling_rate))


@dataclass
class Timeline:
    instant: Time = Time(seconds=0)

    def __rshift__(
        self, seconds: Numeric | Time
    ) -> Self:  # Logic for Bitwise right shift operation of track duration
        self.instant += seconds
        return self


@dataclass
class MeasuredTimeline(Timeline):
    measure: Time = Time(seconds=0)
    last_measure_ended_at: Time = field(init=False, repr=False)

    def __post_init__(self) -> None:  # Logic to calculate time instance of last bar
        if self.measure.seconds > 0 and self.instant.seconds > 0:
            periods = self.instant.seconds // self.measure.seconds
            self.last_measure_ended_at = Time(periods * self.measure.seconds)
        else:
            self.last_measure_ended_at = Time(seconds=0)

    def __next__(self) -> Self:  # To jumpt to next bar
        if self.measure.seconds <= 0:
            raise ValueError("measure duration must be positive")
        self.last_measure_ended_at += self.measure
        self.instant = self.last_measure_ended_at
        return self
