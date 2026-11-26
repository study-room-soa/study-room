from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    room_id = Column(Integer, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="confirmed"
    )