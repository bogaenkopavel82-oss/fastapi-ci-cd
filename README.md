# FastAPI CI/CD

Проект с настройкой CI/CD для FastAPI приложения.

## Линтеры

- isort — сортировка импортов
- black — форматирование кода
- flake8 — проверка стиля и ошибок
- mypy — проверка типов

## Запуск

```bash
uvicorn app.main:app --reload