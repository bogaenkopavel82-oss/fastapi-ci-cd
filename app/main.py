"""
Главный модуль FastAPI приложения для управления парковками.
"""
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

# Создаем таблицы в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parking API",
    description="API для управления парковками и клиентами",
    version="1.0.0",
)


@app.get("/clients", response_model=List[schemas.Client])
def get_clients(db: Session = Depends(get_db)):
    """Получить список всех клиентов."""
    return crud.get_clients(db)


@app.get("/clients/{client_id}", response_model=schemas.Client)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Получить информацию о клиенте по ID."""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.post("/clients", response_model=schemas.ClientCreateResponse, status_code=201)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    """Создать нового клиента."""
    db_client = crud.create_client(db, client)
    return {"id": db_client.id, "message": "Client created"}


@app.post("/parkings", response_model=schemas.ParkingCreateResponse, status_code=201)
def create_parking(parking: schemas.ParkingCreate, db: Session = Depends(get_db)):
    """Создать новую парковку."""
    db_parking = crud.create_parking(db, parking)
    return {"id": db_parking.id, "message": "Parking created"}


@app.post(
    "/client_parkings", response_model=schemas.ParkingEntryResponse, status_code=201
)
def enter_parking(entry: schemas.ParkingEntry, db: Session = Depends(get_db)):
    """Заезд клиента на парковку."""
    client = crud.get_client(db, entry.client_id)
    parking = crud.get_parking(db, entry.parking_id)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")
    if not parking.opened:
        raise HTTPException(status_code=400, detail="Parking is closed")
    if parking.count_available_places <= 0:
        raise HTTPException(status_code=400, detail="No available places")

    existing_session = crud.get_active_session(db, entry.client_id, entry.parking_id)
    if existing_session:
        raise HTTPException(status_code=400, detail="Client already on this parking")

    session = crud.create_parking_session(db, entry.client_id, entry.parking_id)

    return {
        "message": "Entered parking",
        "client_id": entry.client_id,
        "parking_id": entry.parking_id,
        "time_in": session.time_in.isoformat(),
    }


@app.delete("/client_parkings")
def exit_parking(client_id: int, parking_id: int, db: Session = Depends(get_db)):
    """Выезд клиента с парковки (параметры через query string)."""
    client = crud.get_client(db, client_id)
    parking = crud.get_parking(db, parking_id)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not parking:
        raise HTTPException(status_code=404, detail="Parking not found")

    session = crud.get_active_session(db, client_id, parking_id)
    if not session:
        raise HTTPException(status_code=400, detail="Client is not on this parking")

    if not client.credit_card:
        raise HTTPException(status_code=400, detail="No credit card linked. Cannot pay")

    completed_session = crud.exit_parking(db, session, parking)

    return {
        "message": "Exited parking",
        "client_id": client_id,
        "parking_id": parking_id,
        "time_in": completed_session.time_in.isoformat(),
        "time_out": completed_session.time_out.isoformat(),
    }
