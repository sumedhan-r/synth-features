"""String instrument playback and song management endpoints."""

from functools import partial

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.api.core.lifespan import get_db
from src.api.schemas.string_instrument import StringPlaybackRequest
from src.api.schemas.string_song import (
    MeasureCreate,
    MeasureResponse,
    SongCreate,
    SongDetailResponse,
    SongListResponse,
    SongResponse,
    TrackCreate,
    TrackDetailResponse,
    TrackResponse,
)
from src.api.services.audio_response import stream_audio
from src.api.services.storages.string_songs import (
    MeasureStorage,
    SongStorage,
    TrackStorage,
)
from src.api.services.strings.playback import synthesize_string_audio
from src.api.services.strings.song import synthesize_song_audio

router = APIRouter()


# ==================== Pattern-Based Playback ====================


@router.post("/playback")
async def stream_string_playback(
    request: StringPlaybackRequest = Body(...),
) -> StreamingResponse:
    """
    Stream string instrument playback audio in real-time.

    Accepts a JSON payload to configure:
    - Instrument settings (preset or custom tuning, vibration, damping)
    - Chord progression (fret positions for each chord)
    - Strumming pattern (stroke directions, durations, and intervals)

    Returns streaming audio/wav file of the synthesized string instrument performance.
    """
    audio_generator = partial(synthesize_string_audio, request)
    return stream_audio(audio_generator, filename="string_playback.wav")


# ==================== Song Management ====================


@router.post("/songs", response_model=SongResponse, status_code=201)
def create_new_song(
    song_data: SongCreate = Body(...), db: Session = Depends(get_db)
) -> SongResponse:
    """
    Create a new song with metadata and timing configuration.

    Args:
        song_data: Song configuration including BPM, time signature, genre, mood
        db: Database session

    Returns:
        Created song details
    """
    song = SongStorage.create(db, song_data)
    return SongResponse.model_validate(song)


@router.get("/songs/{song_id}", response_model=SongDetailResponse)
def get_song_details(
    song_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> SongDetailResponse:
    """
    Get song details with all tracks, measures, and events.

    Args:
        song_id: Song ID
        db: Database session

    Returns:
        Song with full hierarchy (tracks → measures → events)

    Raises:
        StringSongNotFoundHTTPException: If song not found
    """
    song = SongStorage.get_with_tracks(db, song_id)
    return SongDetailResponse.model_validate(song)


@router.get("/songs", response_model=SongListResponse)
def list_songs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> SongListResponse:
    """
    List all songs with pagination.

    Args:
        skip: Number of songs to skip
        limit: Maximum number of songs to return
        db: Database session

    Returns:
        List of songs
    """
    songs = SongStorage.get_all(db, skip=skip, limit=limit)
    return SongListResponse(songs=[SongResponse.model_validate(s) for s in songs])


@router.delete("/songs/{song_id}", status_code=204)
def delete_song_by_id(
    song_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> None:
    """
    Delete a song and all its measures/strokes.

    Args:
        song_id: Song ID
        db: Database session

    Raises:
        StringSongNotFoundHTTPException: If song not found
    """
    SongStorage.delete(db, song_id)


# ==================== Track Management ====================


@router.post("/songs/{song_id}/tracks", response_model=TrackResponse, status_code=201)
def create_track(
    song_id: int = Path(..., gt=0),
    track_data: TrackCreate = Body(...),
    db: Session = Depends(get_db),
) -> TrackResponse:
    """
    Create a new track for a song.

    Args:
        song_id: Song ID
        track_data: Track configuration (instrument, mix settings)
        db: Database session

    Returns:
        Created track details

    Raises:
        StringSongNotFoundHTTPException: If song not found
    """
    # Verify song exists (raises if not found)
    SongStorage.get(db, song_id)

    track = TrackStorage.create(db, song_id, track_data)
    return TrackResponse.model_validate(track)


@router.get("/tracks/{track_id}", response_model=TrackDetailResponse)
def get_track_details(
    track_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> TrackDetailResponse:
    """
    Get track details with all measures and events.

    Args:
        track_id: Track ID
        db: Database session

    Returns:
        Track with measures and events

    Raises:
        Exception: If track not found
    """
    track = TrackStorage.get_with_measures(db, track_id)
    return TrackDetailResponse.model_validate(track)


@router.delete("/tracks/{track_id}", status_code=204)
def delete_track(
    track_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> None:
    """
    Delete a track and all its measures/events.

    Args:
        track_id: Track ID
        db: Database session

    Raises:
        Exception: If track not found
    """
    TrackStorage.delete(db, track_id)


# ==================== Measure Management ====================


@router.post(
    "/tracks/{track_id}/measures", response_model=MeasureResponse, status_code=201
)
def add_measure_to_track(
    track_id: int = Path(..., gt=0),
    measure_data: MeasureCreate = Body(...),
    db: Session = Depends(get_db),
) -> MeasureResponse:
    """
    Add a measure with events to a track.

    Args:
        track_id: Track ID
        measure_data: Measure configuration with events
        db: Database session

    Returns:
        Created measure with events

    Raises:
        Exception: If track not found
    """
    # Verify track exists (raises if not found)
    TrackStorage.get(db, track_id)

    measure = MeasureStorage.create(db, track_id, measure_data)
    return MeasureResponse.model_validate(measure)


@router.delete("/tracks/{track_id}/measures/{measure_id}", status_code=204)
def delete_measure_by_id(
    track_id: int = Path(..., gt=0),
    measure_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a measure and all its events.

    Args:
        track_id: Track ID
        measure_id: Measure ID
        db: Database session

    Raises:
        StringMeasureNotFoundHTTPException: If measure not found or doesn't belong to track
    """
    MeasureStorage.delete(db, measure_id, track_id)


# ==================== Synthesis ====================


@router.post("/tracks/{track_id}/synthesize")
async def synthesize_track_endpoint(
    track_id: int = Path(..., gt=0), db: Session = Depends(get_db)
) -> StreamingResponse:
    """
    Synthesize a track and stream the audio.

    Retrieves the track from the database, converts measures/events to audio using
    the Karplus-Strong algorithm, and streams the result.

    Args:
        track_id: Track ID to synthesize
        db: Database session

    Returns:
        Streaming audio/wav file

    Raises:
        Exception: If track not found
        StringSongNoMeasuresHTTPException: If track has no measures
    """
    # Get track to get song_id and track name
    track = TrackStorage.get(db, track_id)
    song_id: int = track.song_id  # type: ignore[assignment]
    track_name: str = track.track_name  # type: ignore[assignment]

    # Create audio generator
    audio_generator = partial(synthesize_song_audio, db, song_id, track_id)
    return stream_audio(audio_generator, filename=f"{track_name.replace(' ', '_')}.wav")
