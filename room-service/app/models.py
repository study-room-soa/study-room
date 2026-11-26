from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    rooms = relationship("Room", back_populates="building")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    building_id = Column(
        Integer,
        ForeignKey("buildings.id"),
        nullable=False
    )
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    building = relationship("Building", back_populates="rooms")