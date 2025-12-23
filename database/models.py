import sqlite3

def create_database() -> bool:
    """Создает SQLite базу данных."""
    db_name = "hh_vacancies.db"

    try:
        conn = sqlite3.connect(db_name)
        conn.close()
        print(f"✅ Файл базы данных SQLite: '{db_name}'")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании файла SQLite: {e}")
        return False


def create_tables() -> bool:
    """Создает таблицы employers и vacancies."""
    db_name = "hh_vacancies.db"

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Создаем таблицу employers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hh_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                url TEXT,
                description TEXT,
                open_vacancies INTEGER DEFAULT 0
            )
        """)

        # Создаем таблицу vacancies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hh_id TEXT UNIQUE NOT NULL,
                employer_id INTEGER,
                title TEXT NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency TEXT,
                city TEXT,
                experience TEXT,
                url TEXT NOT NULL,
                published_at TEXT,
                FOREIGN KEY (employer_id) REFERENCES employers (employer_id)
            )
        """)

        # Создаем индексы
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id ON vacancies(employer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vacancies_salary ON vacancies(salary_from, salary_to)")

        conn.commit()

        # Проверяем создание таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("✅ Таблицы успешно созданы")
        print(f"✅ Создано таблиц: {len(tables)}/2")
        for table in tables:
            print(f"   - {table[0]}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Создание базы данных и таблиц")
    print("=" * 50)

    if create_database():
        create_tables()
    else:
        print("❌ Не удалось создать базу данных")

    print("=" * 50)