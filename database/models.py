import psycopg
from psycopg import sql
from psycopg.errors import DuplicateDatabase, OperationalError

from database.config import DBConfig


def create_database() -> bool:
    """
    Создает базу данных если не существует.
    Возвращает True если база существует или создана успешно.
    """
    connection = None

    try:
        # Получаем конфигурацию
        config = DBConfig.get_db_config()
        db_name = config.get("dbname", "hh_vacancies")

        print(f"🔍 Проверяем существование базы данных '{db_name}'...")

        # Подключаемся к системной базе данных 'postgres'
        config_no_db = {
            "host": config.get("host", "localhost"),
            "port": config.get("port", "5432"),
            "user": config.get("user", "postgres"),
            "password": config.get("password", "postgres"),
            "dbname": "postgres",  # Подключаемся к стандартной базе
        }

        connection = psycopg.connect(**config_no_db)
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Проверяем существование базы данных
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))

            if cursor.fetchone():
                print(f"✅ База данных '{db_name}' уже существует")
                return True
            else:
                # Создаем базу данных если ее нет
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                print(f"✅ База данных '{db_name}' создана")
                return True

    except DuplicateDatabase:
        # Получаем имя базы данных для сообщения
        config = DBConfig.get_db_config()
        db_name = config.get("dbname", "hh_vacancies")
        print(f"✅ База данных '{db_name}' уже существует")
        return True
    except OperationalError as error:
        print(f"❌ Ошибка подключения к PostgreSQL: {error}")
        return False
    except Exception as error:
        print(f"❌ Неожиданная ошибка при создании базы данных: {error}")
        return False
    finally:
        if connection:
            connection.close()


def create_tables() -> bool:
    """Создает таблицы employers и vacancies."""
    connection = None

    try:
        config = DBConfig.get_db_config()
        connection = psycopg.connect(**config)

        with connection.cursor() as cursor:
            # Таблица employers (упрощенная версия)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id SERIAL PRIMARY KEY,
                    hh_id VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    url TEXT,
                    description TEXT,
                    open_vacancies INTEGER DEFAULT 0
                )
            """
            )

            # Таблица vacancies (упрощенная версия)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    hh_id VARCHAR(50) UNIQUE NOT NULL,
                    employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE,
                    title VARCHAR(500) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    city VARCHAR(100),
                    experience VARCHAR(100),
                    url TEXT NOT NULL,
                    published_at TIMESTAMP
                )
            """
            )

            # Индексы для производительности
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id
                ON vacancies(employer_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_salary
                ON vacancies(salary_from, salary_to)
            """
            )

        connection.commit()
        print("✅ Таблицы успешно созданы")
        return True

    except OperationalError as error:
        print(f"❌ Ошибка подключения к базе данных: {error}")
        return False
    except Exception as error:
        print(f"❌ Ошибка при создании таблиц: {error}")
        return False
    finally:
        if connection:
            connection.close()


def clear_tables() -> bool:
    """Очищает все данные из таблиц."""
    connection = None

    try:
        connection = psycopg.connect(**DBConfig.get_db_config())

        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE")
            cursor.execute("TRUNCATE TABLE employers RESTART IDENTITY CASCADE")

        connection.commit()
        print("✅ Таблицы очищены")
        return True

    except OperationalError as error:
        print(f"❌ Ошибка подключения к базе данных: {error}")
        return False
    except Exception as error:
        print(f"❌ Ошибка при очистке таблиц: {error}")
        return False
    finally:
        if connection:
            connection.close()


def drop_database() -> bool:
    """Удаляет базу данных (опасно!)."""
    connection = None

    try:
        config = DBConfig.get_db_config()
        db_name = config.get("dbname", "hh_vacancies")

        config_no_db = {
            "host": config.get("host", "localhost"),
            "port": config.get("port", "5432"),
            "user": config.get("user", "postgres"),
            "password": config.get("password", "postgres"),
            "dbname": "postgres",
        }

        connection = psycopg.connect(**config_no_db)
        connection.autocommit = True

        with connection.cursor() as cursor:
            # Завершаем все соединения с БД
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """,
                (db_name,),
            )

            cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))

        print(f"✅ База данных '{db_name}' удалена")
        return True

    except OperationalError as error:
        print(f"❌ Ошибка подключения к PostgreSQL: {error}")
        return False
    except Exception as error:
        print(f"❌ Ошибка при удалении базы данных: {error}")
        return False
    finally:
        if connection:
            connection.close()


def initialize_database() -> bool:
    """Инициализирует базу данных и таблицы."""
    print("\n" + "=" * 50)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ POSTGRESQL")
    print("=" * 50)

    if not DBConfig.check_config():
        print("❌ Неверная конфигурация базы данных")
        return False

    # Создаем базу данных
    if not create_database():
        print("❌ Не удалось создать базу данных")
        return False

    # Создаем таблицы
    return create_tables()


if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("\n🎯 Инициализация базы данных завершена успешно!")
    else:
        print("\n❌ Инициализация базы данных завершена с ошибками")
