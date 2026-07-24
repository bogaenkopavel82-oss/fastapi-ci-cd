from flask import Flask

from app.models import db


def create_app():
    app = Flask(__name__)

    # Конфигурация
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = False

    # Инициализация db
    db.init_app(app)

    # Регистрация роутов
    from app.routes import bp

    app.register_blueprint(bp)

    return app
