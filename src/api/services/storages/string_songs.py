"""Database storage layer for songs, tracks, measures, and events."""

import json
from fractions import Fraction

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.api.core.exceptions.storage import (
    StringMeasureNotFoundHTTPException,
    StringSongNotFoundHTTPException,
)
from src.api.core.lifespan import get_async_session_factory
from src.api.schemas.string_song import (
    MeasureCreate,
    SongCreate,
    TrackCreate,
)
from src.db.user_db.models.event import Event
from src.db.user_db.models.measure import Measure
from src.db.user_db.models.song import Song
from src.db.user_db.models.track import Track


# ==================== Song Storage ====================


class SongStorage:
    """Storage operations for songs."""

    @staticmethod
    async def create(song_data: SongCreate) -> Song:
        """
        Create a new song in the database.

        Args:
            song_data: Song creation data

        Returns:
            Created Song instance
        """
        async with get_async_session_factory()() as session:
            # Parse note value fraction
            note_value = Fraction(song_data.note_value)

            song = Song(
                title=song_data.title,
                artist=song_data.artist,
                bpm=song_data.bpm,
                beats_per_measure=song_data.beats_per_measure,
                note_value_numerator=note_value.numerator,
                note_value_denominator=note_value.denominator,
                genre=song_data.genre,
                mood=song_data.mood,
                harmonic_style=song_data.harmonic_style,
                rhythmic_style=song_data.rhythmic_style,
            )

            session.add(song)
            await session.commit()
            await session.refresh(song)

            return song

    @staticmethod
    async def get(song_id: int) -> Song:
        """
        Retrieve a song by ID.

        Args:
            song_id: Song ID

        Returns:
            Song instance

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(select(Song).filter(Song.id == song_id))
            song = result.scalar_one_or_none()
            if not song:
                raise StringSongNotFoundHTTPException(song_id)
            return song

    @staticmethod
    async def get_with_tracks(song_id: int) -> Song:
        """
        Retrieve a song with all tracks, measures, and events eagerly loaded.

        Args:
            song_id: Song ID

        Returns:
            Song instance with full hierarchy loaded

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(
                select(Song)
                .options(
                    joinedload(Song.tracks)
                    .joinedload(Track.measures)
                    .joinedload(Measure.events)
                )
                .filter(Song.id == song_id)
            )
            song = result.scalar_one_or_none()
            if not song:
                raise StringSongNotFoundHTTPException(song_id)
            return song

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 100) -> list[Song]:
        """
        Retrieve all songs with pagination.

        Args:
            skip: Number of songs to skip
            limit: Maximum number of songs to return

        Returns:
            List of Song instances
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(select(Song).offset(skip).limit(limit))
            return list(result.scalars().all())

    @staticmethod
    async def delete(song_id: int) -> None:
        """
        Delete a song and all its tracks/measures/events (cascade).

        Args:
            song_id: Song ID

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(select(Song).filter(Song.id == song_id))
            song = result.scalar_one_or_none()
            if not song:
                raise StringSongNotFoundHTTPException(song_id)

            await session.delete(song)
            await session.commit()


# ==================== Track Storage ====================


class TrackStorage:
    """Storage operations for tracks."""

    @staticmethod
    async def create(song_id: int, track_data: TrackCreate) -> Track:
        """
        Create a new track for a song.

        Args:
            song_id: Song ID
            track_data: Track creation data

        Returns:
            Created Track instance
        """
        async with get_async_session_factory()() as session:
            # Convert instrument_config dict to JSON string if present
            instrument_config_json = (
                json.dumps(track_data.instrument_config)
                if track_data.instrument_config
                else None
            )

            track = Track(
                song_id=song_id,
                track_number=track_data.track_number,
                track_name=track_data.track_name,
                instrument_category=track_data.instrument_category,
                instrument_type=track_data.instrument_type,
                instrument_config=instrument_config_json,
                volume=track_data.volume,
                pan=track_data.pan,
            )

            session.add(track)
            await session.commit()
            await session.refresh(track)

            return track

    @staticmethod
    async def get(track_id: int) -> Track:
        """
        Retrieve a track by ID.

        Args:
            track_id: Track ID

        Returns:
            Track instance

        Raises:
            ValueError: If track not found (TODO: Add custom exception)
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(select(Track).filter(Track.id == track_id))
            track = result.scalar_one_or_none()
            if not track:
                raise ValueError(f"Track with ID {track_id} not found")
            return track

    @staticmethod
    async def get_with_measures(track_id: int) -> Track:
        """
        Retrieve a track with all measures and events.

        Args:
            track_id: Track ID

        Returns:
            Track with measures and events loaded

        Raises:
            ValueError: If track not found (TODO: Add custom exception)
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(
                select(Track)
                .options(joinedload(Track.measures).joinedload(Measure.events))
                .filter(Track.id == track_id)
            )
            track = result.scalar_one_or_none()
            if not track:
                raise ValueError(f"Track with ID {track_id} not found")
            return track

    @staticmethod
    async def delete(track_id: int) -> None:
        """
        Delete a track and all its measures/events (cascade).

        Args:
            track_id: Track ID

        Raises:
            ValueError: If track not found (TODO: Add custom exception)
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(select(Track).filter(Track.id == track_id))
            track = result.scalar_one_or_none()
            if not track:
                raise ValueError(f"Track with ID {track_id} not found")

            await session.delete(track)
            await session.commit()


# ==================== Measure Storage ====================


class MeasureStorage:
    """Storage operations for measures."""

    @staticmethod
    async def create(track_id: int, measure_data: MeasureCreate) -> Measure:
        """
        Create a new measure with events for a track.

        Args:
            track_id: Track ID
            measure_data: Measure creation data with events

        Returns:
            Created Measure instance
        """
        async with get_async_session_factory()() as session:
            # Create measure
            measure = Measure(
                track_id=track_id, measure_number=measure_data.measure_number
            )

            session.add(measure)
            await session.flush()  # Get measure ID without committing

            # Create events for this measure
            for idx, event_data_obj in enumerate(measure_data.events):
                event = Event(
                    measure_id=measure.id,
                    event_order=idx,
                    note_duration=event_data_obj.note_duration,
                    event_data=json.dumps(event_data_obj.event_data),
                )
                session.add(event)

            await session.commit()
            await session.refresh(measure)

            return measure

    @staticmethod
    async def get(measure_id: int, track_id: int | None = None) -> Measure:
        """
        Retrieve a measure with its events.

        Args:
            measure_id: Measure ID
            track_id: Optional track ID to verify ownership

        Returns:
            Measure instance with events

        Raises:
            StringMeasureNotFoundHTTPException: If measure not found or doesn't belong to track
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(
                select(Measure)
                .options(joinedload(Measure.events))
                .filter(Measure.id == measure_id)
            )
            measure = result.scalar_one_or_none()
            if not measure:
                raise StringMeasureNotFoundHTTPException(measure_id, track_id or 0)
            if track_id is not None and measure.track_id != track_id:
                raise StringMeasureNotFoundHTTPException(measure_id, track_id)
            return measure

    @staticmethod
    async def delete(measure_id: int, track_id: int) -> None:
        """
        Delete a measure and all its events (cascade).

        Args:
            measure_id: Measure ID
            track_id: Track ID to verify ownership

        Raises:
            StringMeasureNotFoundHTTPException: If measure not found or doesn't belong to track
        """
        async with get_async_session_factory()() as session:
            result = await session.execute(
                select(Measure).filter(Measure.id == measure_id)
            )
            measure = result.scalar_one_or_none()
            if not measure or measure.track_id != track_id:
                raise StringMeasureNotFoundHTTPException(measure_id, track_id)

            await session.delete(measure)
            await session.commit()
