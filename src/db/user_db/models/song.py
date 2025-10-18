"""Song database model."""

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from src.db.user_db.models.base import Base


class Song(Base):
    """
    Song model representing a complete musical composition.

    Contains metadata, timing configuration, and categorization.
    A song can have multiple instrument tracks playing simultaneously.
    """

    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)

    # Timing configuration (global for all tracks)
    bpm = Column(Float, nullable=False)  # Beats per minute
    beats_per_measure = Column(
        Integer, nullable=False
    )  # Top of time signature (e.g., 4 for 4/4)
    note_value_numerator = Column(
        Integer, nullable=False
    )  # Bottom numerator (e.g., 1 for 1/4)
    note_value_denominator = Column(
        Integer, nullable=False
    )  # Bottom denominator (e.g., 4 for 1/4)

    # Categorization
    genre = Column(String, nullable=True)  # "rock", "jazz", "classical", "blues", etc.
    mood = Column(String, nullable=True)  # "energetic", "calm", "melancholic", "upbeat"
    harmonic_style = Column(
        String, nullable=True
    )  # "modal", "tonal", "atonal", "pentatonic"
    rhythmic_style = Column(
        String, nullable=True
    )  # "syncopated", "straight", "swing", "polyrhythmic"

    # Relationships
    tracks = relationship(
        "Track",
        back_populates="song",
        cascade="all, delete-orphan",
        order_by="Track.track_number",
    )
