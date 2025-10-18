"""String instrument business logic custom exceptions."""

from enum import Enum

from starlette.status import HTTP_400_BAD_REQUEST

from src.api.core.exception import CustomHTTPException, CustomHTTPExceptionInfo


class StringHTTPExceptionInfos(Enum):
    """
    String instrument business logic custom HTTP exception information.

    Error Code Range: 3000-3999
    """

    STRING_SONG_NO_MEASURES = CustomHTTPExceptionInfo(
        HTTP_400_BAD_REQUEST,
        "CUSTERR3001",
        "String song has no measures",
        "Cannot synthesize string song with no measures",
    )


# ==================== Exception Classes ====================


class StringSongNoMeasuresHTTPException(CustomHTTPException):
    """Exception raised when attempting to synthesize a string song with no measures."""

    def __init__(self, song_id: int) -> None:
        info = StringHTTPExceptionInfos.STRING_SONG_NO_MEASURES.value
        super().__init__(
            status_code=info.status_code,
            error_code=info.error_code,
            detail=f"{info.detail} (Song ID: {song_id})",
            log_detail=f"{info.log_detail}. Song ID: {song_id}",
        )
