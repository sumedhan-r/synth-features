"""Factory for creating string instruments from various configurations."""

import json

from src.api.core.config import get_config
from src.api.schemas.string_instrument import (
    CustomInstrumentRequest,
    InstrumentType,
    StringPlaybackRequest,
)
from src.db.user_db.models.track import Track
from src.tools.instruments.strings.plucked import PluckedStringInstrument, StringTuning
from src.tools.utils.temporal import Time


def create_instrument_from_request(
    request: StringPlaybackRequest,
) -> PluckedStringInstrument:
    """
    Create instrument from API request configuration.

    Args:
        request: User request containing instrument type or custom settings

    Returns:
        Configured PluckedStringInstrument instance
    """
    if isinstance(request, CustomInstrumentRequest):
        # Use custom settings from request
        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*request.tuning_notes),
            vibration=Time(seconds=request.vibration_seconds),
            damping=request.damping,
        )
    else:
        # Use preset from config
        config = get_config()
        if request.instrument_type == InstrumentType.UKULELE:
            preset = config.string_instruments.ukulele
        else:  # InstrumentType.GUITAR
            preset = config.string_instruments.guitar

        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*preset.tuning),
            vibration=Time(seconds=preset.vibration_seconds),
            damping=preset.damping,
        )


def create_instrument_from_track(track: Track) -> PluckedStringInstrument:
    """
    Create instrument from track database model.

    Args:
        track: Track database model

    Returns:
        Configured PluckedStringInstrument instance
    """
    # Parse instrument config from JSON if present
    config_json: str | None = track.instrument_config  # type: ignore[assignment]

    if config_json:
        # Custom instrument configuration
        config_dict = json.loads(config_json)
        tuning_notes = config_dict.get("tuning_notes", [])
        vibration_seconds = config_dict.get("vibration_seconds", 6.0)
        damping = config_dict.get("damping", 0.495)

        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*tuning_notes),
            vibration=Time(seconds=vibration_seconds),
            damping=damping,
        )
    else:
        # Use preset from config based on instrument_type
        app_config = get_config()
        instrument_type_str: str = track.instrument_type  # type: ignore[assignment]

        if instrument_type_str == "ukulele":
            preset = app_config.string_instruments.ukulele
        else:  # guitar or default
            preset = app_config.string_instruments.guitar

        return PluckedStringInstrument(
            tuning=StringTuning.from_notes(*preset.tuning),
            vibration=Time(seconds=preset.vibration_seconds),
            damping=preset.damping,
        )
