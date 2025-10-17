"""String instrument playback endpoints."""

from functools import partial

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from src.api.schemas.string_instrument import StringPlaybackRequest
from src.api.services.audio_response import stream_audio
from src.api.services.string_playback import synthesize_string_audio

router = APIRouter()


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
