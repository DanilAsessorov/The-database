import psycopg2


def test_connection():
    print("=" * 50)
    print("Тестирование подключения к PostgreSQL 18")
    print("=" * 50)

    # Пробуем разные порты
    ports = [5433, 5432]

    for port in ports:
        print(f"\nПробуем порт {port}...")
        try:
            conn = psycopg2.connect(
                dbname="postgres", user="postgres", password="", host="localhost", port=port  # твой пароль
            )

            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                print(f"✅ УСПЕХ! PostgreSQL на порту {port}")
                print(f"   Версия: {version}")

            conn.close()
            return port

        except psycopg2.OperationalError as e:
            print(f"❌ Не удалось подключиться к порту {port}: {e}")

    print("\n" + "=" * 50)
    print("РЕКОМЕНДАЦИЯ:")
    print("Используйте SQLite для быстрого старта:")
    print("В файле .env укажите:")
    print("DB_TYPE=sqlite")
    print("DB_NAME=hh_vacancies.db")
    print("=" * 50)
    return None


if __name__ == "__main__":
    port = test_connection()
    if port:
        print(f"\n🎯 Используйте порт {port} в файле .env")
