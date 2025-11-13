"""Song synthesis service for string instruments."""

import json
from fractions import Fraction
from typing import Iterator

from src.api.core.exceptions.strings import StringSongNoMeasuresHTTPException
from src.api.services.storages.string_songs import SongStorage
from src.api.services.strings.instrument_factory import create_instrument_from_track
from src.api.services.strings.synthesis import synthesize_strokes
from src.tools.instruments.strings.chord import Chord
from src.tools.instruments.strings.stroke import StrokeVelocity
from src.tools.utils.temporal import MeasuredTimeline, Time


def _calculate_note_duration(note_duration_str: str, beat_duration: Time) -> Time:
    """
    Calculate actual time duration for a note based on BPM.

    Args:
        note_duration_str: Note duration as fraction string (e.g., "3/16")
        beat_duration: Duration of one beat

    Returns:
        Time duration for the note
    """
    fraction = Fraction(note_duration_str)
    return beat_duration * (fraction * 4)  # Multiply by 4 to normalize to quarter note


async def _build_track_strokes(
    song_id: int, track_id: int
) -> list[tuple[Time, Chord, StrokeVelocity]]:
    """
    Build strokes with timeline from track's measures and events.

    Args:
        song_id: Song ID
        track_id: Track ID

    Returns:
        List of (instant, chord, stroke_velocity) tuples

    Raises:
        StringSongNotFoundHTTPException: If song not found
        StringSongNoMeasuresHTTPException: If track has no measures
    """
    # Fetch song with all tracks and their data
    song = await SongStorage.get_with_tracks(song_id)

    # Find the specific track
    track = next((t for t in song.tracks if t.id == track_id), None)
    if not track or not track.measures:
        raise StringSongNoMeasuresHTTPException(song_id)

    # Calculate timing based on song configuration
    bpm: float = song.bpm  # type: ignore[assignment]
    beats_per_measure: int = song.beats_per_measure  # type: ignore[assignment]

    beat_duration = Time(seconds=60 / bpm)
    measure_duration = beat_duration * beats_per_measure

    # Create timeline with measure tracking
    timeline = MeasuredTimeline(measure=measure_duration)

    # Build list of strokes
    strokes: list[tuple[Time, Chord, StrokeVelocity]] = []

    # Process each measure in order
    for measure_model in sorted(track.measures, key=lambda m: m.measure_number):
        # Move to next measure if not the first one
        if measure_model.measure_number > 1:
            next(timeline)

        # Process each event in the measure
        for event_model in sorted(measure_model.events, key=lambda e: e.event_order):
            # Parse event_data JSON
            event_data_str: str = event_model.event_data  # type: ignore[assignment]
            event_data = json.loads(event_data_str)

            # Extract string-specific data
            fret_positions = event_data.get("fret_positions", [])
            direction = event_data.get("direction", "down")
            speed_milliseconds = event_data.get("speed_milliseconds", 40.0)

            # Create chord and stroke velocity
            chord = Chord.from_numbers(*fret_positions)
            stroke_time = Time.from_milliseconds(speed_milliseconds)

            if direction == "down":
                velocity = StrokeVelocity.down(stroke_time)
            else:
                velocity = StrokeVelocity.up(stroke_time)

            # Add stroke with current instant
            strokes.append((timeline.instant, chord, velocity))

            # Advance timeline by note duration
            note_duration_str: str = event_model.note_duration  # type: ignore[assignment]
            note_duration = _calculate_note_duration(note_duration_str, beat_duration)
            timeline >> note_duration

    return strokes


async def synthesize_song_audio(
    song_id: int, track_id: int, chunk_size: int = 8192
) -> Iterator[bytes]:
    """
    Synthesize a single track from a song and yield audio chunks.

    Args:
        song_id: Song ID
        track_id: Track ID to synthesize
        chunk_size: Size of audio chunks to yield in bytes

    Yields:
        Audio data chunks as bytes

    Raises:
        StringSongNotFoundHTTPException: If song not found
        StringSongNoMeasuresHTTPException: If track has no measures
    """
    # Fetch song with tracks to get the specific track
    song = await SongStorage.get_with_tracks(song_id)

    # Find the specific track
    track = next((t for t in song.tracks if t.id == track_id), None)
    if not track:
        raise ValueError(f"Track with ID {track_id} not found in song {song_id}")

    # Create instrument from track configuration
    instrument = create_instrument_from_track(track)

    # Build strokes from track's measures and events
    strokes = await _build_track_strokes(song_id, track_id)

    # Use shared synthesis function
    return synthesize_strokes(instrument, strokes, chunk_size)
