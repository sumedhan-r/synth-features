from itertools import cycle
from typing import Iterator

from src.api.schemas.string_instrument import (
    StrokeConfig,
    StrokeDirection,
    StringPlaybackRequest,
    StrummingPattern,
)
from src.api.services.strings.instrument_factory import create_instrument_from_request
from src.api.services.strings.synthesis import synthesize_strokes
from src.tools.instruments.strings.chord import Chord
from src.tools.instruments.strings.stroke import StrokeVelocity
from src.tools.utils.temporal import Time, Timeline


def _create_stroke_velocity(config: StrokeConfig) -> StrokeVelocity:
    """
    Convert StrokeConfig to StrokeVelocity.

    Args:
        config: Stroke configuration from request

    Returns:
        StrokeVelocity object for synthesis
    """
    time = Time.from_milliseconds(config.milliseconds)
    if config.direction == StrokeDirection.DOWN:
        return StrokeVelocity.down(time)
    return StrokeVelocity.up(time)


def _build_pattern_strokes(
    pattern: StrummingPattern,
) -> Iterator[tuple[Time, Chord, StrokeVelocity]]:
    """
    Build strokes with timeline from strumming pattern configuration.

    Args:
        pattern: Strumming pattern configuration

    Yields:
        Tuple of (instant, chord, stroke_velocity)
    """
    # Convert fret positions to Chord objects
    chords = [Chord.from_numbers(*chord.positions) for chord in pattern.chords]

    # Convert stroke configurations to StrokeVelocity objects
    strokes = [_create_stroke_velocity(stroke) for stroke in pattern.strokes]

    # Create interval cycle from user input
    intervals = cycle(pattern.intervals)

    # Build strokes with timeline tracking
    timeline = Timeline()
    for chord in chords:
        for _ in range(pattern.chord_repeat_count):
            for stroke in strokes:
                yield timeline.instant, chord, stroke
                timeline >> next(intervals)


def synthesize_string_audio(
    request: StringPlaybackRequest, chunk_size: int = 8192
) -> Iterator[bytes]:
    """
    Synthesize string instrument audio from pattern-based request.

    Args:
        request: User configuration for instrument and strumming pattern
        chunk_size: Size of audio chunks to yield in bytes

    Yields:
        Audio data chunks as bytes
    """
    # Create instrument and convert pattern to strokes
    instrument = create_instrument_from_request(request)
    strokes = _build_pattern_strokes(request.pattern)

    # Use shared synthesis function
    return synthesize_strokes(instrument, strokes, chunk_size)
