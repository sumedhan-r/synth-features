from itertools import cycle
from typing import Iterator

from src.api.core.config import get_config
from src.api.schemas.chorus import (
    ChorusRequest,
    CustomInstrumentRequest,
    InstrumentType,
)
from src.api.services.samples import AudioTrack
from src.tools.instrument.guitar import PluckedStringInstrument, StringTuning
from src.tools.signals.string_synthesis import StringSynthesizer
from src.tools.utils.chord import Chord
from src.tools.utils.processing import normalize
from src.tools.utils.stroke import StrokeVelocity
from src.tools.utils.temporal import Time, Timeline


def get_instrument(request: ChorusRequest) -> PluckedStringInstrument:
    """
    Create instrument from request configuration.

    Args:
        request: User request containing instrument type or custom settings

    Returns:
        Configured PluckedStringInstrument instance
    """
    if isinstance(request, CustomInstrumentRequest):
        # Use custom settings from request
        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*request.tuning_notes),
            vibration=Time(seconds=request.vibration_seconds),
            damping=request.damping,
        )
    else:
        # Use preset from config
        config = get_config()
        if request.instrument_type == InstrumentType.UKULELE:
            preset = config.string_instruments.ukulele
        else:  # InstrumentType.GUITAR
            preset = config.string_instruments.guitar

        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*preset.tuning),
            vibration=Time(seconds=preset.vibration_seconds),
            damping=preset.damping,
        )


def strumming_pattern(
    request: ChorusRequest,
) -> Iterator[tuple[float, Chord, StrokeVelocity]]:
    """
    Generate strumming pattern from user configuration.

    Args:
        request: User configuration for chords, strokes, and intervals

    Yields:
        Tuple of (interval, chord, stroke_velocity)
    """
    # Convert chord configurations to Chord objects
    chords = [
        Chord.from_numbers(*chord.fret_positions) for chord in request.pattern.chords
    ]

    # Convert stroke configurations to StrokeVelocity objects
    strokes = []
    for stroke_config in request.pattern.strokes:
        time = Time.from_milliseconds(stroke_config.milliseconds)
        if stroke_config.direction.lower() == "down":
            strokes.append(StrokeVelocity.down(time))
        elif stroke_config.direction.lower() == "up":
            strokes.append(StrokeVelocity.up(time))
        else:
            raise ValueError(
                f"Invalid stroke direction: {stroke_config.direction}. Must be 'up' or 'down'"
            )

    # Create interval cycle from user input
    interval = cycle(request.pattern.intervals)

    # Generate pattern
    for chord in chords:
        for _ in range(request.pattern.chord_repeat_count):
            for stroke in strokes:
                yield next(interval), chord, stroke


def create_chorus(request: ChorusRequest) -> Iterator[bytes]:
    """
    Generate chorus audio from user configuration and yield chunks as bytes.

    Args:
        request: User configuration for instrument and strumming pattern

    Yields:
        Audio data chunks as bytes
    """
    # Create instrument (from preset or custom settings)
    instrument = get_instrument(request)
    synthesizer = StringSynthesizer(instrument=instrument)
    audio_track = AudioTrack(synthesizer.sampling_rate)
    timeline = Timeline()

    # Generate audio from user's strumming pattern
    for interval, chord, stroke in strumming_pattern(request):
        audio_samples = synthesizer.strum_strings(chord, stroke)
        audio_track.add_at(timeline.instant, audio_samples)
        timeline >> interval

    output = normalize(audio_track.samples)

    # Yield audio data in chunks
    chunk_size = 8192
    for i in range(0, len(output), chunk_size):
        chunk = output[i : i + chunk_size]
        yield chunk.tobytes()
