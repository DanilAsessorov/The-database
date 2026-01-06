import os
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()


class DBConfig:
    """Конфигурация базы данных PostgreSQL."""

    @staticmethod
    def get_db_config() -> Dict[str, Any]:
        """Возвращает конфигурацию для подключения."""
        return {
            "dbname": os.getenv("DB_NAME", "hh_vacancies"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }

    @staticmethod
    def check_config() -> bool:
        """Проверяет наличие необходимых переменных окружения."""
        required = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]

        for var in required:
            if not os.getenv(var):
                print(f"❌ Отсутствует переменная окружения: {var}")
                return False

        print("✅ Конфигурация PostgreSQL проверена")
        return True
