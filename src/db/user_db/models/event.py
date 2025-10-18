"""Event database model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.user_db.models.base import Base


class Event(Base):
    """
    Event model representing a musical event (note, chord, stroke, hit, etc.) in a measure.

    Stores timing and event data polymorphically based on instrument category.
    Event data format varies by instrument type.
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    measure_id = Column(Integer, ForeignKey("measures.id"), nullable=False, index=True)
    event_order = Column(Integer, nullable=False)  # Order within measure (0, 1, 2, ...)

    # Timing
    note_duration = Column(String, nullable=False)  # "3/16", "1/8", "7/16", etc.

    # Polymorphic event data (JSON string, format depends on instrument_category)
    # For strings: {"fret_positions": [0, 0, 2, 2, 0, null], "direction": "down", "speed_milliseconds": 40}
    # For winds: {"pitch": "C4", "dynamics": "forte", "articulation": "staccato", "duration_milliseconds": 200}
    # For percussion: {"drum_type": "kick", "velocity": 0.8, "duration_milliseconds": 50}
    event_data = Column(String, nullable=False)

    # Relationships
    measure = relationship("Measure", back_populates="events")
