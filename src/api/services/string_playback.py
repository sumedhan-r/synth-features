from itertools import cycle
from typing import Iterator

from src.api.core.config import get_config
from src.api.schemas.string_instrument import (
    CustomInstrumentRequest,
    InstrumentType,
    StrokeConfig,
    StrokeDirection,
    StringPlaybackRequest,
    StrummingPattern,
)
from src.tools.audio.track import AudioTrack
from src.tools.instruments.strings.chord import Chord
from src.tools.instruments.strings.plucked import PluckedStringInstrument, StringTuning
from src.tools.instruments.strings.stroke import StrokeVelocity
from src.tools.synthesis.physical_modeling.karplus_strong import StringSynthesizer
from src.tools.utils.processing import normalize
from src.tools.utils.temporal import Time, Timeline


def get_instrument(request: StringPlaybackRequest) -> PluckedStringInstrument:
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


def build_strumming_pattern(
    pattern: StrummingPattern,
) -> Iterator[tuple[float, Chord, StrokeVelocity]]:
    """
    Build strumming pattern from configuration.

    Args:
        pattern: Strumming pattern configuration

    Yields:
        Tuple of (interval, chord, stroke_velocity)
    """
    # Convert fret positions to Chord objects
    chords = [Chord.from_numbers(*chord.positions) for chord in pattern.chords]

    # Convert stroke configurations to StrokeVelocity objects
    strokes = [_create_stroke_velocity(stroke) for stroke in pattern.strokes]

    # Create interval cycle from user input
    intervals = cycle(pattern.intervals)

    # Generate pattern
    for chord in chords:
        for _ in range(pattern.chord_repeat_count):
            for stroke in strokes:
                yield next(intervals), chord, stroke


def synthesize_string_audio(
    request: StringPlaybackRequest, chunk_size: int = 8192
) -> Iterator[bytes]:
    """
    Synthesize string instrument audio from request configuration.

    Args:
        request: User configuration for instrument and strumming pattern
        chunk_size: Size of audio chunks to yield in bytes

    Yields:
        Audio data chunks as bytes
    """
    # Create instrument (from preset or custom settings)
    instrument = get_instrument(request)
    synthesizer = StringSynthesizer(instrument=instrument)
    audio_track = AudioTrack(synthesizer.sampling_rate)
    timeline = Timeline()

    # Generate audio from user's strumming pattern
    for interval, chord, stroke in build_strumming_pattern(request.pattern):
        audio_samples = synthesizer.strum_strings(chord, stroke)
        audio_track.add_at(timeline.instant, audio_samples)
        timeline >> interval

    output = normalize(audio_track.samples)

    # Yield audio data in chunks
    for i in range(0, len(output), chunk_size):
        chunk = output[i : i + chunk_size]
        yield chunk.tobytes()
