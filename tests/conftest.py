"""
Фикстуры для тестов.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base, Client, Parking

# Используем файловую БД
TEST_DATABASE_URL = "sqlite:///./test_parking.db"

# Удаляем старый файл если есть
if os.path.exists("test_parking.db"):
    try:
        os.remove("test_parking.db")
    except PermissionError:
        pass

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределяем зависимость get_db для тестов."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создает таблицы один раз для всех тестов."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Не удаляем файл, чтобы избежать PermissionError
    # if os.path.exists("test_parking.db"):
    #     os.remove("test_parking.db")


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для сессии БД."""
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента FastAPI."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_client(db_session):
    """Создает тестового клиента в БД."""
    client = Client(
        name="Test",
        surname="User",
        credit_card="1234-5678-9012-3456",
        car_number="A123BC",
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture(scope="function")
def test_parking(db_session):
    """Создает тестовую парковку в БД."""
    parking = Parking(
        address="Test Street, 1",
        opened=True,
        count_places=10,
        count_available_places=10,
    )
    db_session.add(parking)
    db_session.commit()
    db_session.refresh(parking)
    return parking
