"""
Тесты API эндпоинтов.
"""
import pytest

from app.models import Client, ClientParking, Parking


@pytest.mark.parametrize(
    "endpoint,expected_status",
    [
        ("/clients", 200),
        ("/clients/1", 200),
    ],
)
def test_get_methods(client, test_client, test_parking, endpoint, expected_status):
    """Проверка, что GET-методы возвращают 200."""
    response = client.get(endpoint)
    assert response.status_code == expected_status


def test_create_client(client, db_session):
    """Проверка создания клиента."""
    data = {
        "name": "John",
        "surname": "Doe",
        "credit_card": "1111-2222-3333-4444",
        "car_number": "XYZ123",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "Client created"

    client_db = db_session.query(Client).filter(Client.name == "John").first()
    assert client_db is not None
    assert client_db.surname == "Doe"


def test_create_parking(client, db_session):
    """Проверка создания парковки."""
    data = {"address": "Main Street, 10", "count_places": 20}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "Parking created"

    parking_db = (
        db_session.query(Parking).filter(Parking.address == "Main Street, 10").first()
    )
    assert parking_db is not None
    assert parking_db.count_places == 20
    assert parking_db.count_available_places == 20


def test_enter_parking(client, db_session, test_client, test_parking):
    """Проверка заезда на парковку."""
    # Обновляем объект из сессии
    db_session.refresh(test_parking)
    available_before = test_parking.count_available_places

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201
    assert response.json()["message"] == "Entered parking"

    # Обновляем объект после запроса
    db_session.refresh(test_parking)
    assert test_parking.count_available_places == available_before - 1

    session = (
        db_session.query(ClientParking)
        .filter(
            ClientParking.client_id == test_client.id,
            ClientParking.parking_id == test_parking.id,
            ClientParking.time_out.is_(None),
        )
        .first()
    )
    assert session is not None


def test_exit_parking(client, db_session, test_client, test_parking):
    """Проверка выезда с парковки."""
    # Сначала создаем запись о заезде
    data_in = {"client_id": test_client.id, "parking_id": test_parking.id}
    client.post("/client_parkings", json=data_in)

    # Обновляем объект из сессии
    db_session.refresh(test_parking)
    available_before = test_parking.count_available_places

    response = client.delete(
        f"/client_parkings?client_id={test_client.id}&parking_id={test_parking.id}"
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Exited parking"

    # Обновляем объект после запроса
    db_session.refresh(test_parking)
    assert test_parking.count_available_places == available_before + 1

    session = (
        db_session.query(ClientParking)
        .filter(
            ClientParking.client_id == test_client.id,
            ClientParking.parking_id == test_parking.id,
        )
        .first()
    )
    assert session.time_out is not None
