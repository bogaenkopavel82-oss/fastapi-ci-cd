import os
import sys
from datetime import datetime

import pytest

from app import create_app
from app.models import Client, ClientParking, Parking
from app.models import db as _db

# Добавляем путь к папке hw
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Фикстура приложения в тестовом режиме"""
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Фикстура тестового клиента"""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Фикстура сессии БД"""
    with app.app_context():
        yield _db


@pytest.fixture
def test_client(db_session):
    """Создает тестового клиента в БД"""
    client = Client(
        name="Test",
        surname="User",
        credit_card="1234-5678-9012-3456",
        car_number="A123BC",
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def test_parking(db_session):
    """Создает тестовую парковку в БД"""
    parking = Parking(
        address="Test Street, 1",
        opened=True,
        count_places=10,
        count_available_places=10,
    )
    db_session.add(parking)
    db_session.commit()
    return parking


@pytest.fixture
def test_client_parking(db_session, test_client, test_parking):
    """Создает тестовую запись о заезде"""
    client_parking = ClientParking(
        client_id=test_client.id, parking_id=test_parking.id, time_in=datetime.utcnow()
    )
    db_session.add(client_parking)
    db_session.commit()
    return client_parking
