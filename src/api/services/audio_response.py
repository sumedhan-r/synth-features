"""Generic audio streaming utilities."""

from typing import Callable, Iterator

from fastapi.responses import StreamingResponse


def stream_audio(
    audio_generator: Callable[[], Iterator[bytes]], filename: str = "audio.wav"
) -> StreamingResponse:
    """
    Generic audio streaming function that accepts any audio generator.

    Args:
        audio_generator: A callable that returns an iterator yielding audio chunks as bytes
        filename: Optional filename for the downloaded audio file

    Returns:
        StreamingResponse with audio/wav content

    Example usage:
        # From create_chorus
        return stream_audio(create_chorus, filename="chorus.wav")

        # From future function
        return stream_audio(your_future_audio_function, filename="reverb.wav")
    """
    return StreamingResponse(
        audio_generator(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache",
        },
    )
