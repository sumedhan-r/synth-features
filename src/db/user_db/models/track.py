"""Track database model."""

from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.user_db.models.base import Base


class Track(Base):
    """
    Track model representing a single instrument part in a song.

    Each track contains instrument configuration and its own measures/events.
    A song can have multiple tracks playing simultaneously (multi-instrumental).
    """

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False, index=True)
    track_number = Column(
        Integer, nullable=False
    )  # Order in arrangement (1, 2, 3, ...)
    track_name = Column(
        String, nullable=False
    )  # "Lead Guitar", "Bass", "Drums", "Piano"

    # Instrument configuration (polymorphic)
    instrument_category = Column(
        String, nullable=False
    )  # "strings", "winds", "percussion", "keyboards", "vocal"
    instrument_type = Column(
        String, nullable=False
    )  # "guitar", "ukulele", "piano", "trumpet", etc.
    instrument_config = Column(
        String, nullable=True
    )  # JSON string with instrument-specific settings

    # Mix settings
    volume = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    pan = Column(Float, default=0.0, nullable=False)  # -1.0 (left) to 1.0 (right)

    # Relationships
    song = relationship("Song", back_populates="tracks")
    measures = relationship(
        "Measure",
        back_populates="track",
        cascade="all, delete-orphan",
        order_by="Measure.measure_number",
    )
