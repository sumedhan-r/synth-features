"""Measure database model."""

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.db.user_db.models.base import Base


class Measure(Base):
    """
    Measure model representing a single bar/measure in a track.

    Contains events that define notes, chords, or rhythmic patterns within one measure.
    """

    __tablename__ = "measures"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    measure_number = Column(Integer, nullable=False)  # 1, 2, 3, ... (order in track)

    # Relationships
    track = relationship("Track", back_populates="measures")
    events = relationship(
        "Event",
        back_populates="measure",
        cascade="all, delete-orphan",
        order_by="Event.event_order",
    )
