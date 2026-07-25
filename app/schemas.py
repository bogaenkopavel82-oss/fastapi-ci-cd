"""
Pydantic схемы для валидации данных.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    """Базовая схема клиента."""

    name: str = Field(..., min_length=1, max_length=50)
    surname: str = Field(..., min_length=1, max_length=50)
    credit_card: Optional[str] = Field(None, max_length=50)
    car_number: Optional[str] = Field(None, max_length=10)


class ClientCreate(ClientBase):
    """Схема для создания клиента."""

    pass


class Client(ClientBase):
    """Схема клиента для ответа."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class ClientCreateResponse(BaseModel):
    """Ответ на создание клиента."""

    id: int
    message: str


class ParkingBase(BaseModel):
    """Базовая схема парковки."""

    address: str = Field(..., min_length=1, max_length=100)
    opened: bool = True
    count_places: int = Field(..., ge=1)


class ParkingCreate(ParkingBase):
    """Схема для создания парковки."""

    pass


class Parking(ParkingBase):
    """Схема парковки для ответа."""

    id: int
    count_available_places: int

    model_config = ConfigDict(from_attributes=True)


class ParkingCreateResponse(BaseModel):
    """Ответ на создание парковки."""

    id: int
    message: str


class ParkingEntry(BaseModel):
    """Схема для заезда на парковку."""

    client_id: int = Field(..., gt=0)
    parking_id: int = Field(..., gt=0)


class ParkingExit(BaseModel):
    """Схема для выезда с парковки."""

    client_id: int = Field(..., gt=0)
    parking_id: int = Field(..., gt=0)


class ParkingEntryResponse(BaseModel):
    """Ответ на заезд."""

    message: str
    client_id: int
    parking_id: int
    time_in: str


class ParkingExitResponse(BaseModel):
    """Ответ на выезд."""

    message: str
    client_id: int
    parking_id: int
    time_in: str
    time_out: str
