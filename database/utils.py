from typing import Any, Dict, List, Optional

import psycopg

from database.config import DBConfig


class DatabaseUtils:
    """Утилиты для работы с PostgreSQL."""

    @staticmethod
    def get_db_connection() -> Optional[psycopg.Connection]:
        """Создает соединение с PostgreSQL."""
        db_config = None
        try:
            db_config = DBConfig.get_db_config()

            # Проверяем обязательные параметры подключения
            required_fields = ["dbname", "user", "host"]
            missing_fields = [field for field in required_fields if not db_config.get(field)]

            if missing_fields:
                print(f"❌ Отсутствуют обязательные параметры: {', '.join(missing_fields)}")
                return None

            connection = psycopg.connect(**db_config)
            return connection

        except psycopg.OperationalError as error:
            print(f"❌ Ошибка подключения к PostgreSQL: {error}")
            if db_config:
                print(f"   Проверьте доступность сервера: {db_config.get('host')}:{db_config.get('port')}")
            return None
        except psycopg.Error as error:
            print(f"❌ Ошибка PostgreSQL: {error}")
            return None

    @staticmethod
    def save_employers_to_db(employers_data: List[Dict[str, Any]]) -> bool:
        """Сохраняет компании в БД."""
        if not employers_data:
            print("⚠️  Нет данных компаний для сохранения")
            return False

        connection = DatabaseUtils.get_db_connection()
        if not connection:
            return False

        try:
            saved_count = 0
            with connection.cursor() as cursor:
                # Упрощенный запрос
                insert_query = """
                    INSERT INTO employers (hh_id, name, url, description, open_vacancies)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (hh_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        open_vacancies = EXCLUDED.open_vacancies
                """

                for employer in employers_data:
                    try:
                        cursor.execute(
                            insert_query,
                            (
                                employer.get("hh_id"),
                                employer.get("name"),
                                employer.get("url", ""),
                                employer.get("description", "")[:500],
                                employer.get("open_vacancies", 0),
                            ),
                        )
                        saved_count += 1
                    except psycopg.Error as error:
                        print(f"⚠️  Ошибка при сохранении компании {employer.get('name')}: {error}")
                        continue

            connection.commit()
            print(f"✅ Сохранено компаний: {saved_count} из {len(employers_data)}")
            return saved_count > 0

        except psycopg.Error as error:
            print(f"❌ Ошибка при сохранении компаний: {error}")
            connection.rollback()
            return False
        finally:
            connection.close()

    @staticmethod
    def save_vacancies_to_db(vacancies_data: List[Dict[str, Any]], employer_mapping: Dict[str, int]) -> bool:
        """Сохраняет вакансии в БД."""
        if not vacancies_data:
            print("⚠️  Нет данных вакансий для сохранения")
            return False

        if not employer_mapping:
            print("⚠️  Отсутствует маппинг компаний")
            return False

        connection = DatabaseUtils.get_db_connection()
        if not connection:
            return False

        try:
            saved_count = 0
            skipped_count = 0

            with connection.cursor() as cursor:
                insert_query = """
                    INSERT INTO vacancies
                    (hh_id, employer_id, title, salary_from, salary_to, currency,
                     city, experience, url, published_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (hh_id) DO UPDATE SET
                        employer_id = EXCLUDED.employer_id,
                        title = EXCLUDED.title,
                        salary_from = EXCLUDED.salary_from,
                        salary_to = EXCLUDED.salary_to,
                        currency = EXCLUDED.currency,
                        city = EXCLUDED.city,
                        experience = EXCLUDED.experience,
                        url = EXCLUDED.url,
                        published_at = EXCLUDED.published_at
                """

                for vacancy in vacancies_data:
                    # Получаем employer_hh_id
                    employer_hh_id = None
                    if "employer" in vacancy:
                        employer_hh_id = vacancy.get("employer", {}).get("id")
                    elif "employer_id" in vacancy:
                        employer_hh_id = vacancy.get("employer_id")

                    if not employer_hh_id:
                        skipped_count += 1
                        continue

                    employer_id = employer_mapping.get(str(employer_hh_id))
                    if not employer_id:
                        skipped_count += 1
                        continue

                    salary_info = vacancy.get("salary") or {}

                    try:
                        cursor.execute(
                            insert_query,
                            (
                                vacancy.get("id"),
                                employer_id,
                                vacancy.get("name", "")[:500],
                                salary_info.get("from"),
                                salary_info.get("to"),
                                salary_info.get("currency"),
                                vacancy.get("area", {}).get("name") if vacancy.get("area") else None,
                                vacancy.get("experience", {}).get("name") if vacancy.get("experience") else None,
                                vacancy.get("alternate_url") or vacancy.get("url", ""),
                                vacancy.get("published_at"),
                            ),
                        )
                        saved_count += 1

                        if saved_count % 50 == 0:
                            connection.commit()
                            print(f"  💾 Промежуточное сохранение: {saved_count} вакансий")

                    except psycopg.Error as error:
                        print(f"⚠️  Ошибка при сохранении вакансии: {error}")
                        continue

            connection.commit()
            print(f"✅ Сохранено вакансий: {saved_count} из {len(vacancies_data)}")
            if skipped_count > 0:
                print(f"⚠️  Пропущено вакансий: {skipped_count}")
            return saved_count > 0

        except psycopg.Error as error:
            print(f"❌ Ошибка при сохранении вакансий: {error}")
            connection.rollback()
            return False
        finally:
            connection.close()

    @staticmethod
    def get_employer_mapping() -> Dict[str, int]:
        """Получает маппинг hh_id -> employer_id."""
        connection = DatabaseUtils.get_db_connection()
        if not connection:
            return {}

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT hh_id, employer_id FROM employers")
                results = cursor.fetchall()
                mapping = {str(hh_id): employer_id for hh_id, employer_id in results}
                return mapping
        except psycopg.Error as error:
            print(f"❌ Ошибка при получении маппинга: {error}")
            return {}
        finally:
            connection.close()


if __name__ == "__main__":
    # Тестируем подключение
    test_connection = DatabaseUtils.get_db_connection()
    if test_connection:
        print("✅ Подключение к PostgreSQL успешно")
        test_connection.close()
    else:
        print("❌ Не удалось подключиться к PostgreSQL")
