"""Chorus audio generation schemas."""

from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, Tag


class InstrumentType(str, Enum):
    """Supported instrument types."""

    UKULELE = "ukulele"
    GUITAR = "guitar"
    CUSTOM = "custom"


class StrokeConfig(BaseModel):
    """Configuration for a single stroke."""

    direction: str = Field(..., description="Stroke direction: 'down' or 'up'")
    milliseconds: float = Field(
        ..., gt=0, description="Stroke duration in milliseconds"
    )


class ChordProgression(BaseModel):
    """Chord progression configuration."""

    fret_positions: list[int] = Field(
        ...,
        description="Fret positions for each string (0 = open string)",
        min_length=4,
        max_length=4,
    )


class StrummingPatternRequest(BaseModel):
    """Request schema for strumming pattern configuration."""

    chords: list[ChordProgression] = Field(
        ...,
        description="List of chords in the progression",
        min_length=1,
        max_length=16,
    )
    strokes: list[StrokeConfig] = Field(
        ..., description="List of strokes in the pattern", min_length=1, max_length=32
    )
    intervals: list[float] = Field(
        ...,
        description="Time intervals between strokes in seconds",
        min_length=1,
        max_length=32,
    )
    chord_repeat_count: int = Field(
        default=2, ge=1, le=10, description="Number of times to repeat each chord"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chords": [
                    {"fret_positions": [0, 0, 0, 3]},
                    {"fret_positions": [0, 2, 3, 2]},
                    {"fret_positions": [2, 0, 0, 0]},
                    {"fret_positions": [2, 0, 1, 0]},
                ],
                "strokes": [
                    {"direction": "down", "milliseconds": 25},
                    {"direction": "down", "milliseconds": 25},
                    {"direction": "up", "milliseconds": 25},
                    {"direction": "up", "milliseconds": 10},
                    {"direction": "down", "milliseconds": 10},
                    {"direction": "up", "milliseconds": 25},
                ],
                "intervals": [0.65, 0.45, 0.75, 0.2, 0.4, 0.25],
                "chord_repeat_count": 2,
            }
        }


class PresetInstrumentRequest(BaseModel):
    """Request schema for preset instruments (ukulele/guitar)."""

    instrument_type: Literal[InstrumentType.UKULELE, InstrumentType.GUITAR] = Field(
        default=InstrumentType.UKULELE,
        description="Type of preset instrument: 'ukulele' or 'guitar'",
    )
    pattern: StrummingPatternRequest = Field(
        ..., description="Strumming pattern configuration"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "instrument_type": "ukulele",
                "pattern": {
                    "chords": [
                        {"fret_positions": [0, 0, 0, 3]},
                        {"fret_positions": [0, 2, 3, 2]},
                    ],
                    "strokes": [
                        {"direction": "down", "milliseconds": 25},
                        {"direction": "up", "milliseconds": 10},
                    ],
                    "intervals": [0.65, 0.45],
                    "chord_repeat_count": 2,
                },
            }
        }


class CustomInstrumentRequest(BaseModel):
    """Request schema for custom instrument configuration."""

    instrument_type: Literal[InstrumentType.CUSTOM] = Field(
        default=InstrumentType.CUSTOM,
        description="Must be 'custom' for custom instrument settings",
    )
    tuning_notes: list[str] = Field(
        ...,
        description="Custom tuning notes. Example: ['E4', 'B3', 'G3', 'D3', 'A2', 'E2']",
        min_length=4,
        max_length=6,
    )
    vibration_seconds: float = Field(
        ...,
        gt=0,
        le=10,
        description="Custom string vibration duration in seconds",
    )
    damping: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Custom string damping factor",
    )
    pattern: StrummingPatternRequest = Field(
        ..., description="Strumming pattern configuration"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "instrument_type": "custom",
                "tuning_notes": ["D4", "A3", "F3", "C3"],
                "vibration_seconds": 4.5,
                "damping": 0.6,
                "pattern": {
                    "chords": [{"fret_positions": [0, 0, 0, 0]}],
                    "strokes": [{"direction": "down", "milliseconds": 30}],
                    "intervals": [1.0],
                    "chord_repeat_count": 1,
                },
            }
        }


# Discriminated union for chorus requests
ChorusRequest = Annotated[
    Union[
        Annotated[PresetInstrumentRequest, Tag("preset")],
        Annotated[CustomInstrumentRequest, Tag("custom")],
    ],
    Discriminator("instrument_type"),
]
