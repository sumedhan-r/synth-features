"""Database storage layer for songs, tracks, measures, and events."""

import json
from fractions import Fraction

from sqlalchemy.orm import Session, joinedload

from src.api.core.exceptions.storage import (
    StringMeasureNotFoundHTTPException,
    StringSongNotFoundHTTPException,
)
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
    def create(db: Session, song_data: SongCreate) -> Song:
        """
        Create a new song in the database.

        Args:
            db: Database session
            song_data: Song creation data

        Returns:
            Created Song instance
        """
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

        db.add(song)
        db.commit()
        db.refresh(song)

        return song

    @staticmethod
    def get(db: Session, song_id: int) -> Song:
        """
        Retrieve a song by ID.

        Args:
            db: Database session
            song_id: Song ID

        Returns:
            Song instance

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            raise StringSongNotFoundHTTPException(song_id)
        return song

    @staticmethod
    def get_with_tracks(db: Session, song_id: int) -> Song:
        """
        Retrieve a song with all tracks, measures, and events eagerly loaded.

        Args:
            db: Database session
            song_id: Song ID

        Returns:
            Song instance with full hierarchy loaded

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        song = (
            db.query(Song)
            .options(
                joinedload(Song.tracks)
                .joinedload(Track.measures)
                .joinedload(Measure.events)
            )
            .filter(Song.id == song_id)
            .first()
        )
        if not song:
            raise StringSongNotFoundHTTPException(song_id)
        return song

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Song]:
        """
        Retrieve all songs with pagination.

        Args:
            db: Database session
            skip: Number of songs to skip
            limit: Maximum number of songs to return

        Returns:
            List of Song instances
        """
        return db.query(Song).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, song_id: int) -> None:
        """
        Delete a song and all its tracks/measures/events (cascade).

        Args:
            db: Database session
            song_id: Song ID

        Raises:
            StringSongNotFoundHTTPException: If song not found
        """
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            raise StringSongNotFoundHTTPException(song_id)
        db.delete(song)
        db.commit()


# ==================== Track Storage ====================


class TrackStorage:
    """Storage operations for tracks."""

    @staticmethod
    def create(db: Session, song_id: int, track_data: TrackCreate) -> Track:
        """
        Create a new track for a song.

        Args:
            db: Database session
            song_id: Song ID
            track_data: Track creation data

        Returns:
            Created Track instance
        """
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

        db.add(track)
        db.commit()
        db.refresh(track)

        return track

    @staticmethod
    def get(db: Session, track_id: int) -> Track:
        """
        Retrieve a track by ID.

        Args:
            db: Database session
            track_id: Track ID

        Returns:
            Track instance

        Raises:
            Exception: If track not found (TODO: Add custom exception)
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise ValueError(f"Track with ID {track_id} not found")
        return track

    @staticmethod
    def get_with_measures(db: Session, track_id: int) -> Track:
        """
        Retrieve a track with all measures and events.

        Args:
            db: Database session
            track_id: Track ID

        Returns:
            Track with measures and events loaded

        Raises:
            Exception: If track not found (TODO: Add custom exception)
        """
        track = (
            db.query(Track)
            .options(joinedload(Track.measures).joinedload(Measure.events))
            .filter(Track.id == track_id)
            .first()
        )
        if not track:
            raise ValueError(f"Track with ID {track_id} not found")
        return track

    @staticmethod
    def delete(db: Session, track_id: int) -> None:
        """
        Delete a track and all its measures/events (cascade).

        Args:
            db: Database session
            track_id: Track ID

        Raises:
            Exception: If track not found (TODO: Add custom exception)
        """
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise ValueError(f"Track with ID {track_id} not found")
        db.delete(track)
        db.commit()


# ==================== Measure Storage ====================


class MeasureStorage:
    """Storage operations for measures."""

    @staticmethod
    def create(db: Session, track_id: int, measure_data: MeasureCreate) -> Measure:
        """
        Create a new measure with events for a track.

        Args:
            db: Database session
            track_id: Track ID
            measure_data: Measure creation data with events

        Returns:
            Created Measure instance
        """
        # Create measure
        measure = Measure(track_id=track_id, measure_number=measure_data.measure_number)

        db.add(measure)
        db.flush()  # Get measure ID without committing

        # Create events for this measure
        for idx, event_data_obj in enumerate(measure_data.events):
            event = Event(
                measure_id=measure.id,
                event_order=idx,
                note_duration=event_data_obj.note_duration,
                event_data=json.dumps(event_data_obj.event_data),
            )
            db.add(event)

        db.commit()
        db.refresh(measure)

        return measure

    @staticmethod
    def get(db: Session, measure_id: int, track_id: int | None = None) -> Measure:
        """
        Retrieve a measure with its events.

        Args:
            db: Database session
            measure_id: Measure ID
            track_id: Optional track ID to verify ownership

        Returns:
            Measure instance with events

        Raises:
            StringMeasureNotFoundHTTPException: If measure not found or doesn't belong to track
        """
        measure = (
            db.query(Measure)
            .options(joinedload(Measure.events))
            .filter(Measure.id == measure_id)
            .first()
        )
        if not measure:
            raise StringMeasureNotFoundHTTPException(measure_id, track_id or 0)
        if track_id is not None and measure.track_id != track_id:
            raise StringMeasureNotFoundHTTPException(measure_id, track_id)
        return measure

    @staticmethod
    def delete(db: Session, measure_id: int, track_id: int) -> None:
        """
        Delete a measure and all its events (cascade).

        Args:
            db: Database session
            measure_id: Measure ID
            track_id: Track ID to verify ownership

        Raises:
            StringMeasureNotFoundHTTPException: If measure not found or doesn't belong to track
        """
        measure = db.query(Measure).filter(Measure.id == measure_id).first()
        if not measure or measure.track_id != track_id:
            raise StringMeasureNotFoundHTTPException(measure_id, track_id)
        db.delete(measure)
        db.commit()
