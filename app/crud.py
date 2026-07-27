"""
Функции для работы с базой данных (CRUD операции).
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    """Получить клиента по ID."""
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_clients(db: Session) -> List[models.Client]:
    """Получить всех клиентов."""
    return db.query(models.Client).all()


def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Создать нового клиента."""
    db_client = models.Client(
        name=client.name,
        surname=client.surname,
        credit_card=client.credit_card,
        car_number=client.car_number,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_parking(db: Session, parking_id: int) -> Optional[models.Parking]:
    """Получить парковку по ID."""
    return db.query(models.Parking).filter(models.Parking.id == parking_id).first()


def create_parking(db: Session, parking: schemas.ParkingCreate) -> models.Parking:
    """Создать новую парковку."""
    db_parking = models.Parking(
        address=parking.address,
        opened=parking.opened,
        count_places=parking.count_places,
        count_available_places=parking.count_places,
    )
    db.add(db_parking)
    db.commit()
    db.refresh(db_parking)
    return db_parking


def get_active_session(
    db: Session, client_id: int, parking_id: int
) -> Optional[models.ClientParking]:
    """Получить активную сессию (без time_out)."""
    return (
        db.query(models.ClientParking)
        .filter(
            models.ClientParking.client_id == client_id,
            models.ClientParking.parking_id == parking_id,
            models.ClientParking.time_out.is_(None),
        )
        .first()
    )


def create_parking_session(
    db: Session, client_id: int, parking_id: int
) -> models.ClientParking:
    """Создать запись о заезде."""
    session = models.ClientParking(
        client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow()
    )
    db.add(session)

    parking = get_parking(db, parking_id)
    if parking:
        parking.count_available_places -= 1

    db.commit()
    db.refresh(session)
    return session


def exit_parking(
    db: Session, session: models.ClientParking, parking: models.Parking
) -> models.ClientParking:
    """Завершить парковочную сессию (выезд)."""
    session.time_out = datetime.utcnow()
    parking.count_available_places += 1

    db.commit()
    db.refresh(session)
    return session
