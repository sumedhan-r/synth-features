"""Chorus streaming endpoint."""

from functools import partial

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from src.api.schemas.chorus import ChorusRequest
from src.api.services.play_chorus import create_chorus
from src.api.services.stream import stream_audio

router = APIRouter()


@router.post("/stream")
async def stream_chorus(request: ChorusRequest = Body(...)) -> StreamingResponse:
    """
    Stream chorus audio in real-time with custom configuration.

    Accepts a JSON payload to configure:
    - Instrument settings (tuning, vibration, damping)
    - Chord progression
    - Strumming pattern (strokes and intervals)

    Returns streaming audio/wav file.
    """
    # Use partial to bind the request to create_chorus
    audio_generator = partial(create_chorus, request)
    return stream_audio(audio_generator, filename="chorus.wav")


# Example: Future endpoint using different audio generator
# @router.post("/stream-reverb")
# async def stream_reverb(request: ReverbRequest = Body(...)) -> StreamingResponse:
#     """Stream audio with reverb effect."""
#     from src.api.services.play_reverb import create_reverb
#     audio_generator = partial(create_reverb, request)
#     return stream_audio(audio_generator, filename="reverb.wav")
