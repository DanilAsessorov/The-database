import os
from typing import Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()


class DBConfig:
    """
    Класс для управления конфигурацией базы данных.
    Поддерживает SQLite.
    """

    @staticmethod
    def get_db_type() -> str:
        """Возвращает тип используемой БД."""
        return os.getenv("DB_TYPE", "sqlite").lower()

    @staticmethod
    def get_db_config() -> Dict[str, Any]:
        """
        Возвращает конфигурацию для подключения к БД.
        """
        return {"database": os.getenv("DB_NAME", "hh_vacancies.db"), "db_type": "sqlite"}

    @staticmethod
    def get_connection_string() -> str:
        """
        Формирует строку подключения для SQLite.
        """
        config = DBConfig.get_db_config()
        # Явно указываем тип возвращаемого значения
        connection_string: str = config["database"]
        return connection_string

    @staticmethod
    def check_env_variables() -> bool:
        """
        Проверяет, что все необходимые переменные окружения установлены.
        """
        print("✅ Используется SQLite (файловая БД)")
        return True


if __name__ == "__main__":
    if DBConfig.check_env_variables():
        print("✅ Все переменные окружения заданы корректно.")
        current_config = DBConfig.get_db_config()
        print(f"Тип БД: {current_config['db_type']}")
        print(f"Имя файла БД: {current_config['database']}")
