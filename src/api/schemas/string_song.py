"""Song, Track, Measure, and Event request/response schemas."""

from typing import Any

from pydantic import BaseModel, Field


# ============== Event Schemas ==============


class EventCreate(BaseModel):
    """Schema for creating an event."""

    note_duration: str = Field(
        ...,
        description="Note duration as fraction (e.g., '3/16', '1/8', '7/16')",
        pattern=r"^\d+/\d+$",
    )
    event_data: dict[str, Any] = Field(
        ...,
        description="Polymorphic event data (format depends on instrument category). "
        "For strings: {fret_positions, direction, speed_milliseconds}. "
        "For winds: {pitch, dynamics, articulation}. "
        "For percussion: {drum_type, velocity}.",
    )


class EventResponse(BaseModel):
    """Schema for event response."""

    id: int
    event_order: int
    note_duration: str
    event_data: dict[str, Any]

    class Config:
        from_attributes = True


# ============== Measure Schemas ==============


class MeasureCreate(BaseModel):
    """Schema for creating a measure with events."""

    measure_number: int = Field(..., ge=1, description="Measure number in track")
    events: list[EventCreate] = Field(
        ..., min_length=1, description="List of events in this measure"
    )


class MeasureResponse(BaseModel):
    """Schema for measure response."""

    id: int
    measure_number: int
    events: list[EventResponse]

    class Config:
        from_attributes = True


# ============== Track Schemas ==============


class TrackCreate(BaseModel):
    """Schema for creating a track."""

    track_number: int = Field(..., ge=1, description="Track number in song arrangement")
    track_name: str = Field(
        ..., min_length=1, description="Track name (e.g., 'Lead Guitar', 'Bass')"
    )

    # Instrument configuration
    instrument_category: str = Field(
        ...,
        description="Instrument category: 'strings', 'winds', 'percussion', 'keyboards', 'vocal'",
    )
    instrument_type: str = Field(
        ..., description="Specific instrument type (e.g., 'guitar', 'ukulele', 'piano')"
    )
    instrument_config: dict[str, Any] | None = Field(
        None,
        description="Instrument-specific configuration as JSON. "
        "For strings: {tuning_notes, vibration_seconds, damping}. "
        "For preset instruments, omit this field.",
    )

    # Mix settings
    volume: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Track volume (0.0 to 1.0)"
    )
    pan: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Stereo pan (-1.0=left, 0.0=center, 1.0=right)",
    )


class TrackResponse(BaseModel):
    """Schema for track response."""

    id: int
    track_number: int
    track_name: str
    instrument_category: str
    instrument_type: str
    instrument_config: dict[str, Any] | None
    volume: float
    pan: float

    class Config:
        from_attributes = True


class TrackDetailResponse(TrackResponse):
    """Schema for detailed track response with measures."""

    measures: list[MeasureResponse]

    class Config:
        from_attributes = True


# ============== Song Schemas ==============


class SongCreate(BaseModel):
    """Schema for creating a song."""

    title: str = Field(..., min_length=1, description="Song title")
    artist: str | None = Field(None, description="Artist name")

    # Timing configuration
    bpm: float = Field(..., gt=0, le=300, description="Beats per minute")
    beats_per_measure: int = Field(
        ..., ge=1, le=16, description="Top of time signature (e.g., 4 for 4/4)"
    )
    note_value: str = Field(
        ...,
        description="Bottom of time signature as fraction (e.g., '1/4')",
        pattern=r"^\d+/\d+$",
    )

    # Categorization
    genre: str | None = Field(
        None, description="Genre (e.g., 'rock', 'jazz', 'classical')"
    )
    mood: str | None = Field(
        None, description="Mood (e.g., 'energetic', 'calm', 'melancholic')"
    )
    harmonic_style: str | None = Field(
        None, description="Harmonic style (e.g., 'modal', 'tonal', 'pentatonic')"
    )
    rhythmic_style: str | None = Field(
        None, description="Rhythmic style (e.g., 'syncopated', 'straight', 'swing')"
    )


class SongResponse(BaseModel):
    """Schema for song response."""

    id: int
    title: str
    artist: str | None
    bpm: float
    beats_per_measure: int
    note_value_numerator: int
    note_value_denominator: int
    genre: str | None
    mood: str | None
    harmonic_style: str | None
    rhythmic_style: str | None

    class Config:
        from_attributes = True


class SongDetailResponse(SongResponse):
    """Schema for detailed song response with tracks."""

    tracks: list[TrackDetailResponse]

    class Config:
        from_attributes = True


class SongListResponse(BaseModel):
    """Schema for listing songs."""

    songs: list[SongResponse]
