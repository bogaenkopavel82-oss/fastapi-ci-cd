import factory
from factory import Faker

from app.models import Client, Parking, db


class ClientFactory(factory.Factory):
    """Фабрика для создания клиентов с сохранением в БД"""

    class Meta:
        model = Client

    name = Faker("first_name")
    surname = Faker("last_name")
    credit_card = Faker("credit_card_number")
    car_number = Faker("license_plate")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Переопределяем создание, чтобы объект сохранялся в БД"""
        obj = model_class(*args, **kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj


class ParkingFactory(factory.Factory):
    """Фабрика для создания парковок с сохранением в БД"""

    class Meta:
        model = Parking

    address = Faker("street_address")
    opened = Faker("boolean", chance_of_getting_true=80)
    count_places = Faker("random_int", min=1, max=50)
    count_available_places = factory.LazyAttribute(lambda obj: obj.count_places)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Переопределяем создание, чтобы объект сохранялся в БД"""
        obj = model_class(*args, **kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj
