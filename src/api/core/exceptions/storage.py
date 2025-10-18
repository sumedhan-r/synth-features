"""Database/Storage layer custom exceptions."""

from enum import Enum

from starlette.status import HTTP_404_NOT_FOUND

from src.api.core.exception import CustomHTTPException, CustomHTTPExceptionInfo


class StorageHTTPExceptionInfos(Enum):
    """
    Database/Storage layer custom HTTP exception information.

    Error Code Range: 2000-2999
    """

    # String Song Storage Errors (2000-2099)
    STRING_SONG_NOT_FOUND = CustomHTTPExceptionInfo(
        HTTP_404_NOT_FOUND,
        "CUSTERR2001",
        "String song not found",
        "Requested string instrument song does not exist in the database",
    )

    STRING_MEASURE_NOT_FOUND = CustomHTTPExceptionInfo(
        HTTP_404_NOT_FOUND,
        "CUSTERR2002",
        "String measure not found",
        "Requested string measure does not exist or does not belong to the specified song",
    )


# ==================== Exception Classes ====================


class StringSongNotFoundHTTPException(CustomHTTPException):
    """Exception raised when a string instrument song is not found in database."""

    def __init__(self, song_id: int) -> None:
        info = StorageHTTPExceptionInfos.STRING_SONG_NOT_FOUND.value
        super().__init__(
            status_code=info.status_code,
            error_code=info.error_code,
            detail=f"{info.detail} (ID: {song_id})",
            log_detail=f"{info.log_detail}. Song ID: {song_id}",
        )


class StringMeasureNotFoundHTTPException(CustomHTTPException):
    """Exception raised when a string measure is not found in database."""

    def __init__(self, measure_id: int, song_id: int) -> None:
        info = StorageHTTPExceptionInfos.STRING_MEASURE_NOT_FOUND.value
        super().__init__(
            status_code=info.status_code,
            error_code=info.error_code,
            detail=f"{info.detail} (Measure ID: {measure_id}, Song ID: {song_id})",
            log_detail=f"{info.log_detail}. Measure ID: {measure_id}, Song ID: {song_id}",
        )
