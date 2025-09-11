import re
from dataclasses import dataclass
from typing import Self

from src.tools.utils.temporal import Hertz


@dataclass(frozen=True)
class Pitch:
    """
    Class representing pitch of a sound. This representation is based only on
    frequency of the sound generated.

    Caution: The representation is [Flawed] since pitch does not only constitute
    frequency, but other inherent factors to instrument being played.
    """

    frequency: Hertz

    @classmethod
    def from_scientific_notation(cls, notation: str) -> Self:
        """
        Converts the numerical value of the frequency to the musical
        notation note.
        """
        if match := re.fullmatch(r"([A-G]#?)(-?\d+)?", notation):
            note = match.group(1)
            octave = int(match.group(2) or 0)
            semitones = "C C# D D# E F F# G G# A A# B".split()
            index = octave * 12 + semitones.index(note) - 57
            return cls(frequency=440.0 * 2 ** (index / 12))
        else:
            raise ValueError(f"Invalid scientific pitch notation: {notation}")

    def adjust(self, num_semitones: int) -> Self:
        """
        Pitch of a sound is adjusted based on semitone change.
        Change in semitone represents a logarithmic change in
        frequency with octave notes being doubled/halved.
        """
        return self.__class__(self.frequency * 2 ** (num_semitones / 12))
