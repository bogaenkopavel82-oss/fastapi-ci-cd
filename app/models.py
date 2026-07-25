"""
SQLAlchemy модели для базы данных.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Client(Base):
    """Модель клиента."""

    __tablename__ = "client"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    credit_card = Column(String(50), nullable=True)
    car_number = Column(String(10), nullable=True)

    parkings = relationship("ClientParking", back_populates="client", lazy="selectin")


class Parking(Base):
    """Модель парковки."""

    __tablename__ = "parking"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(100), nullable=False)
    opened = Column(Boolean, default=True)
    count_places = Column(Integer, nullable=False)
    count_available_places = Column(Integer, nullable=False)

    clients = relationship("ClientParking", back_populates="parking", lazy="selectin")


class ClientParking(Base):
    """Модель парковочной сессии."""

    __tablename__ = "client_parking"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    parking_id = Column(Integer, ForeignKey("parking.id"), nullable=False)
    time_in = Column(DateTime, default=datetime.utcnow)
    time_out = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="parkings")
    parking = relationship("Parking", back_populates="clients")

    __table_args__ = (
        UniqueConstraint("client_id", "parking_id", name="unique_client_parking"),
    )
