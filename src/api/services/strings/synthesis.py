"""Core synthesis functions for string instruments."""

from typing import Iterator

from src.tools.audio.track import AudioTrack
from src.tools.instruments.strings.chord import Chord
from src.tools.instruments.strings.plucked import PluckedStringInstrument
from src.tools.instruments.strings.stroke import StrokeVelocity
from src.tools.synthesis.physical_modeling.karplus_strong import StringSynthesizer
from src.tools.utils.processing import normalize
from src.tools.utils.temporal import Time


def synthesize_strokes(
    instrument: PluckedStringInstrument,
    strokes: Iterator[tuple[Time, Chord, StrokeVelocity]],
    chunk_size: int = 8192,
) -> Iterator[bytes]:
    """
    Core synthesis function that generates audio from instrument and stroke sequence.

    This is the shared synthesis logic used by both pattern-based playback
    and song-based synthesis.

    Args:
        instrument: Configured plucked string instrument
        strokes: Iterator yielding (instant, chord, velocity) tuples
        chunk_size: Size of audio chunks to yield in bytes

    Yields:
        Audio data chunks as bytes
    """
    synthesizer = StringSynthesizer(instrument=instrument)
    audio_track = AudioTrack(synthesizer.sampling_rate)

    # Generate audio from strokes
    for instant, chord, velocity in strokes:
        audio_samples = synthesizer.strum_strings(chord, velocity)
        audio_track.add_at(instant, audio_samples)

    # Normalize and yield audio chunks
    output = normalize(audio_track.samples)

    for i in range(0, len(output), chunk_size):
        chunk = output[i : i + chunk_size]
        yield chunk.tobytes()
