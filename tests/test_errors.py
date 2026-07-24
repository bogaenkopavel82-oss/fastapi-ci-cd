import time

from app.models import ClientParking, Parking


def test_enter_closed_parking(client, test_client, db_session):
    """Заезд на закрытую парковку"""
    parking = Parking(
        address="Closed Street", opened=False, count_places=5, count_available_places=5
    )
    db_session.add(parking)
    db_session.commit()

    data = {"client_id": test_client.id, "parking_id": parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 400
    assert response.json["error"] == "Parking is closed"


def test_enter_without_credit_card(client, db_session, test_client, test_parking):
    """Заезд клиента без привязанной карты"""
    test_client.credit_card = None
    db_session.commit()

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201


def test_exit_without_credit_card(
    client, db_session, test_client, test_parking, test_client_parking
):
    """Выезд клиента без привязанной карты"""
    test_client.credit_card = None
    db_session.commit()

    data = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.delete("/client_parkings", json=data)
    assert response.status_code == 400
    assert response.json["error"] == "No credit card linked. Cannot pay"


def test_enter_full_parking(client, db_session, test_client):
    """Заезд на парковку, когда нет свободных мест"""
    parking = Parking(
        address="Full Street", opened=True, count_places=1, count_available_places=1
    )
    db_session.add(parking)
    db_session.commit()

    data = {"client_id": test_client.id, "parking_id": parking.id}
    response = client.post("/client_parkings", json=data)
    assert response.status_code == 201

    response = client.post("/client_parkings", json=data)
    assert response.status_code == 400
    assert response.json["error"] == "No available places"


def test_time_out_after_time_in(client, db_session, test_client, test_parking):
    """Проверка, что время выезда всегда позже времени заезда"""
    data_in = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.post("/client_parkings", json=data_in)
    assert response.status_code == 201

    session = ClientParking.query.filter_by(
        client_id=test_client.id, parking_id=test_parking.id, time_out=None
    ).first()
    time_in = session.time_in

    time.sleep(1)

    data_out = {"client_id": test_client.id, "parking_id": test_parking.id}
    response = client.delete("/client_parkings", json=data_out)
    assert response.status_code == 200

    session = ClientParking.query.filter_by(
        client_id=test_client.id, parking_id=test_parking.id
    ).first()
    assert session.time_out > time_in
