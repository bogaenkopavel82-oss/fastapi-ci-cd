from app.models import Client, Parking
from tests.factories import ClientFactory, ParkingFactory


def test_create_client_with_factory(db_session):
    """Создание клиента через фабрику"""
    client = ClientFactory()

    assert client.id is not None
    assert client.name is not None
    assert client.surname is not None
    assert client.credit_card is not None
    assert client.car_number is not None

    client_db = Client.query.get(client.id)
    assert client_db is not None
    assert client_db.name == client.name


def test_create_parking_with_factory(db_session):
    """Создание парковки через фабрику"""
    parking = ParkingFactory()

    assert parking.id is not None
    assert parking.address is not None
    assert parking.count_places > 0
    assert parking.count_available_places == parking.count_places

    parking_db = Parking.query.get(parking.id)
    assert parking_db is not None
    assert parking_db.address == parking.address


def test_create_multiple_clients(db_session):
    """Создание нескольких клиентов"""
    clients = ClientFactory.create_batch(5)

    assert len(clients) == 5
    for client in clients:
        assert client.id is not None
        assert client.name is not None


def test_create_parking_with_closed_status(db_session):
    """Создание закрытой парковки"""
    parking = ParkingFactory(opened=False)

    assert parking.id is not None
    assert parking.opened is False
    assert parking.count_available_places == parking.count_places


def test_create_client_without_card(db_session):
    """Создание клиента без карты"""
    client = ClientFactory(credit_card=None)

    assert client.credit_card is None
    assert client.id is not None
