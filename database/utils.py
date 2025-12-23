import sys
import os

# Добавляем корень проекта в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from typing import List, Dict, Any, Optional

# Импортируем config с другим именем
try:
    from database.config import DBConfig as Config

    DB_CONFIG_AVAILABLE = True
except ImportError:
    # Если не удается импортировать, создаем простую заглушку
    class Config:
        @staticmethod
        def get_db_config() -> dict:
            return {"database": "hh_vacancies.db"}

    print("⚠️  Используется упрощенная конфигурация")
    DB_CONFIG_AVAILABLE = False


class DatabaseUtils:
    """
    Вспомогательный класс для операций с базой данных SQLite.
    """

    @staticmethod
    def get_db_connection() -> Optional[sqlite3.Connection]:
        """
        Устанавливает соединение с базой данных SQLite.

        Returns:
            Connection object или None в случае ошибки
        """
        try:
            config = Config.get_db_config()
            db_path = config["database"]
            connection = sqlite3.connect(db_path)
            return connection
        except sqlite3.Error as e:
            print(f"❌ Ошибка подключения к базе данных SQLite: {e}")
            return None

    # ... остальной код без изменений, убедись, что везде используется Config, а не DBConfig

    @staticmethod
    def save_employers_to_db(employers_data: List[Dict[str, Any]]) -> bool:
        """
        Сохраняет данные компаний в базу данных SQLite.

        Args:
            employers_data: Список словарей с данными компаний

        Returns:
            bool: True если сохранение прошло успешно
        """
        if not employers_data:
            print("❌ Нет данных для сохранения")
            return False

        db_connection = DatabaseUtils.get_db_connection()
        if not db_connection:
            return False

        try:
            cursor = db_connection.cursor()

            # SQL запрос для вставки данных в SQLite
            insert_query = """
                INSERT OR REPLACE INTO employers
                (hh_id, name, url, description, open_vacancies)
                VALUES (?, ?, ?, ?, ?)
            """

            # Подготавливаем данные для вставки
            prepared_data = []
            for employer in employers_data:
                row = (
                    employer.get("hh_id"),
                    employer.get("name"),
                    employer.get("url"),
                    employer.get("description"),
                    employer.get("open_vacancies", 0),
                )
                prepared_data.append(row)

            # Пакетная вставка
            cursor.executemany(insert_query, prepared_data)

            db_connection.commit()
            print(f"✅ Сохранено компаний: {len(prepared_data)}")
            return True

        except sqlite3.Error as e:
            print(f"❌ Ошибка при сохранении компаний: {e}")
            db_connection.rollback()
            return False
        finally:
            db_connection.close()

    @staticmethod
    def save_vacancies_to_db(vacancies_data: List[Dict[str, Any]], employer_mapping: Dict[str, int]) -> bool:
        """
        Сохраняет вакансии в базу данных SQLite.

        Args:
            vacancies_data: Список словарей с данными вакансий
            employer_mapping: Словарь соответствия hh_id компании -> employer_id в БД

        Returns:
            bool: True если сохранение прошло успешно
        """
        if not vacancies_data:
            print("❌ Нет вакансий для сохранения")
            return False

        db_connection = DatabaseUtils.get_db_connection()
        if not db_connection:
            return False

        try:
            cursor = db_connection.cursor()

            # Подготавливаем данные для вставки
            prepared_vacancies = []

            for vacancy in vacancies_data:
                employer_hh_id = vacancy.get("employer", {}).get("id")
                if not employer_hh_id:
                    continue

                employer_id = employer_mapping.get(str(employer_hh_id))
                if not employer_id:
                    continue

                # Обработка зарплаты
                salary_info = vacancy.get("salary")
                salary_from = salary_info.get("from") if salary_info else None
                salary_to = salary_info.get("to") if salary_info else None
                currency = salary_info.get("currency") if salary_info else None

                # Обработка даты публикации
                published_at = vacancy.get("published_at")

                prepared_vacancy = (
                    vacancy.get("id"),
                    employer_id,
                    vacancy.get("name"),
                    salary_from,
                    salary_to,
                    currency,
                    vacancy.get("area", {}).get("name") if vacancy.get("area") else None,
                    vacancy.get("experience", {}).get("name") if vacancy.get("experience") else None,
                    vacancy.get("alternate_url"),
                    published_at,
                )

                prepared_vacancies.append(prepared_vacancy)

            if not prepared_vacancies:
                print("❌ Нет вакансий с корректными данными для сохранения")
                return False

            # SQL запрос для вставки вакансий в SQLite
            insert_query = """
                INSERT OR REPLACE INTO vacancies
                (hh_id, employer_id, title, salary_from, salary_to, currency,
                 city, experience, url, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Пакетная вставка
            cursor.executemany(insert_query, prepared_vacancies)

            db_connection.commit()
            print(f"✅ Сохранено вакансий: {len(prepared_vacancies)}")
            return True

        except sqlite3.Error as e:
            print(f"❌ Ошибка при сохранении вакансий: {e}")
            db_connection.rollback()
            return False
        finally:
            db_connection.close()

    @staticmethod
    def get_employer_mapping() -> Dict[str, int]:
        """
        Получает словарь соответствия hh_id -> employer_id из базы данных SQLite.

        Returns:
            Dict[str, int]: Словарь с соответствиями ID
        """
        db_connection = DatabaseUtils.get_db_connection()
        if not db_connection:
            return {}

        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT hh_id, employer_id FROM employers")
            mapping = {str(hh_id): employer_id for hh_id, employer_id in cursor.fetchall()}
            return mapping
        except sqlite3.Error as e:
            print(f"❌ Ошибка при получении данных компаний: {e}")
            return {}
        finally:
            db_connection.close()


if __name__ == "__main__":
    # Тестируем подключение
    connection = DatabaseUtils.get_db_connection()
    if connection:
        print("✅ Подключение к базе данных SQLite успешно")
        connection.close()
    else:
        print("❌ Не удалось подключиться к базе данных")
