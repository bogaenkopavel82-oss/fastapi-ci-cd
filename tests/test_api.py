import pytest

from app.models import Client, ClientParking, Parking


# 1. Проверка GET-методов через параметризацию
@pytest.mark.parametrize(
    "endpoint,expected_status",
    [
        ("/clients", 200),
        ("/clients/1", 200),
    ],
)
def test_get_methods(client, test_client, test_parking, endpoint, expected_status):
    """Проверка, что GET-методы возвращают 200"""
    response = client.get(endpoint)
    assert response.status_code == expected_status


# 2. Тест создания клиента
def test_create_client(client, db_session):
    """Проверка создания клиента"""
    data = {
        "name": "John",
        "surname": "Doe",
        "credit_card": "1111-2222-3333-4444",
        "car_number": "XYZ123",
    }
    response = client.post("/clients", json=data)
    assert response.status_code == 201
    assert response.json["message"] == "Client created"

    client_db = Client.query.filter_by(name="John").first()
    assert client_db is not None
    assert client_db.surname == "Doe"
    assert client_db.credit_card == "1111-2222-3333-4444"


# 3. Тест создания парковки
def test_create_parking(client, db_session):
    """Проверка создания парковки"""
    data = {"address": "Main Street, 10", "count_places": 20}
    response = client.post("/parkings", json=data)
    assert response.status_code == 201
    assert response.json["message"] == "Parking created"

    parking_db = Parking.query.filter_by(address="Main Street, 10").first()
    assert parking_db is not None
    assert parking_db.count_places == 20
    assert parking_db.count_available_places == 20


# 4. Тест заезда на парковку
def test_enter_parking(client, db_session, test_client, test_parking):
    """Проверка заезда на парковку"""
    parking_before = Parking.query.get(test_parking.id)
    available_before = parking_before.count_available_places
    assert available_before > 0

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201
    assert response.json["message"] == "Entered parking"

    parking_after = Parking.query.get(test_parking.id)
    assert parking_after.count_available_places == available_before - 1

    session = ClientParking.query.filter_by(
        client_id=test_client.id, parking_id=test_parking.id, time_out=None
    ).first()
    assert session is not None


# 5. Тест выезда с парковки
def test_exit_parking(
    client, db_session, test_client, test_parking, test_client_parking
):
    """Проверка выезда с парковки"""
    parking_before = Parking.query.get(test_parking.id)
    available_before = parking_before.count_available_places

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.delete("/client_parkings", json=data)
    assert response.status_code == 200
    assert response.json["message"] == "Exited parking"

    parking_after = Parking.query.get(test_parking.id)
    assert parking_after.count_available_places == available_before + 1

    session = ClientParking.query.filter_by(
        client_id=test_client.id, parking_id=test_parking.id
    ).first()
    assert session.time_out is not None
