from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models import Client, ClientParking, Parking, db

bp = Blueprint("api", __name__)


# GET /clients — список всех клиентов
@bp.route("/clients", methods=["GET"])
def get_clients():
    clients = Client.query.all()
    return (
        jsonify(
            [
                {
                    "id": c.id,
                    "name": c.name,
                    "surname": c.surname,
                    "credit_card": c.credit_card,
                    "car_number": c.car_number,
                }
                for c in clients
            ]
        ),
        200,
    )


# GET /clients/<int:client_id> — информация клиента
@bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    return (
        jsonify(
            {
                "id": client.id,
                "name": client.name,
                "surname": client.surname,
                "credit_card": client.credit_card,
                "car_number": client.car_number,
            }
        ),
        200,
    )


# POST /clients — создать клиента
@bp.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json()

    # Базовая валидация
    if not data.get("name") or not data.get("surname"):
        return jsonify({"error": "Name and surname are required"}), 400

    client = Client(
        name=data["name"],
        surname=data["surname"],
        credit_card=data.get("credit_card"),
        car_number=data.get("car_number"),
    )

    db.session.add(client)
    db.session.commit()

    return jsonify({"id": client.id, "message": "Client created"}), 201


# POST /parkings — создать парковку
@bp.route("/parkings", methods=["POST"])
def create_parking():
    data = request.get_json()

    if not data.get("address") or not data.get("count_places"):
        return jsonify({"error": "Address and count_places are required"}), 400

    parking = Parking(
        address=data["address"],
        opened=data.get("opened", True),
        count_places=data["count_places"],
        count_available_places=data["count_places"],  # Изначально все места свободны
    )

    db.session.add(parking)
    db.session.commit()

    return jsonify({"id": parking.id, "message": "Parking created"}), 201


# POST /client_parkings — заезд на парковку
@bp.route("/client_parkings", methods=["POST"])
def enter_parking():
    data = request.get_json()
    client_id = data.get("client_id")
    parking_id = data.get("parking_id")

    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id are required"}), 400

    client = Client.query.get(client_id)
    parking = Parking.query.get(parking_id)

    if not client or not parking:
        return jsonify({"error": "Client or Parking not found"}), 404

    # Проверка: открыта ли парковка
    if not parking.opened:
        return jsonify({"error": "Parking is closed"}), 400

    # Проверка: есть ли свободные места
    if parking.count_available_places <= 0:
        return jsonify({"error": "No available places"}), 400

    # Проверка: не находится ли уже клиент на этой парковке
    existing = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id, time_out=None
    ).first()

    if existing:
        return jsonify({"error": "Client already on this parking"}), 400

    # Создаем запись о заезде
    client_parking = ClientParking(
        client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow()
    )

    # Уменьшаем количество свободных мест
    parking.count_available_places -= 1

    db.session.add(client_parking)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Entered parking",
                "client_id": client_id,
                "parking_id": parking_id,
                "time_in": client_parking.time_in.isoformat(),
            }
        ),
        201,
    )


# DELETE /client_parkings — выезд с парковки
@bp.route("/client_parkings", methods=["DELETE"])
def exit_parking():
    data = request.get_json()
    client_id = data.get("client_id")
    parking_id = data.get("parking_id")

    if not client_id or not parking_id:
        return jsonify({"error": "client_id and parking_id are required"}), 400

    client = Client.query.get(client_id)
    parking = Parking.query.get(parking_id)

    if not client or not parking:
        return jsonify({"error": "Client or Parking not found"}), 404

    # Находим активную сессию парковки
    session = ClientParking.query.filter_by(
        client_id=client_id, parking_id=parking_id, time_out=None
    ).first()

    if not session:
        return jsonify({"error": "Client is not on this parking"}), 400

    # Проверка: у клиента есть карта для оплаты
    if not client.credit_card:
        return jsonify({"error": "No credit card linked. Cannot pay"}), 400

    # Проставляем время выезда
    session.time_out = datetime.utcnow()

    # Увеличиваем количество свободных мест
    parking.count_available_places += 1

    db.session.commit()

    return (
        jsonify(
            {
                "message": "Exited parking",
                "client_id": client_id,
                "parking_id": parking_id,
                "time_in": session.time_in.isoformat(),
                "time_out": session.time_out.isoformat(),
            }
        ),
        200,
    )
