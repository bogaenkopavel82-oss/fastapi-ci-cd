"""
Тесты обработки ошибок.
"""
import time

from app.models import ClientParking, Parking


def test_enter_closed_parking(client, test_client, db_session):
    """Заезд на закрытую парковку."""
    parking = Parking(
        address="Closed Street", opened=False, count_places=5, count_available_places=5
    )
    db_session.add(parking)
    db_session.commit()
    db_session.refresh(parking)

    data = {"client_id": test_client.id, "parking_id": parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Parking is closed"


def test_enter_without_credit_card(client, db_session, test_client, test_parking):
    """Заезд клиента без привязанной карты (должен работать)."""
    test_client.credit_card = None
    db_session.commit()

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201


def test_exit_without_credit_card(client, db_session, test_client, test_parking):
    """Выезд клиента без привязанной карты (должен вернуть ошибку)."""
    # Сначала создаем запись о заезде
    data_in = {"client_id": test_client.id, "parking_id": test_parking.id}
    client.post("/client_parkings", json=data_in)

    test_client.credit_card = None
    db_session.commit()

    response = client.delete(
        f"/client_parkings?client_id={test_client.id}&parking_id={test_parking.id}"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "No credit card linked. Cannot pay"


def test_enter_full_parking(client, db_session, test_client):
    """Заезд на парковку, когда нет свободных мест."""
    parking = Parking(
        address="Full Street", opened=True, count_places=1, count_available_places=1
    )
    db_session.add(parking)
    db_session.commit()
    db_session.refresh(parking)

    data = {"client_id": test_client.id, "parking_id": parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201

    # Обновляем объект после заезда
    db_session.refresh(parking)
    assert parking.count_available_places == 0

    # Пытаемся заехать второй раз
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "No available places"


def test_time_out_after_time_in(client, db_session, test_client, test_parking):
    """Проверка, что время выезда всегда позже времени заезда."""
    data_in = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data_in)
    assert response.status_code == 201

    # Обновляем сессию
    db_session.refresh(test_client)
    db_session.refresh(test_parking)

    # Получаем сессию парковки
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
    time_in = session.time_in

    time.sleep(1)

    response = client.delete(
        f"/client_parkings?client_id={test_client.id}&parking_id={test_parking.id}"
    )
    assert response.status_code == 200

    # Обновляем сессию после выезда
    db_session.refresh(session)
    assert session.time_out is not None
    assert session.time_out > time_in
