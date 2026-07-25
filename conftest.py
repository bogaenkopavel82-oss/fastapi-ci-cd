"""
Корневой конфигурационный файл для pytest.
Добавляет путь к проекту в PYTHONPATH.
"""
import os
import sys

# Добавляем корневую папку проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))