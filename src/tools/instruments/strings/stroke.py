from dataclasses import dataclass
from typing import Self

from src.tools.instruments.strings.chord import Chord
from src.tools.utils.enum import StrokeDirection
from src.tools.utils.temporal import Time


@dataclass(frozen=True)
class StrokeVelocity:
    stroke_direction: StrokeDirection
    delay: Time

    @classmethod
    def down(cls, delay: Time) -> Self:
        return cls(StrokeDirection.DOWN, delay)

    @classmethod
    def up(cls, delay: Time) -> Self:
        return cls(StrokeDirection.UP, delay)


@dataclass(frozen=True)
class Stroke:
    instant: Time
    chord: Chord
    velocity: StrokeVelocity
