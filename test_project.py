import sys
import os

# Добавляем текущую директорию в путь поиска модулей
sys.path.append('.')


def test_database_config():
    """Тестирует конфигурацию базы данных."""
    print("=" * 50)
    print("Тестирование конфигурации базы данных")
    print("=" * 50)

    try:
        from database.config import DBConfig
        config = DBConfig.get_db_config()
        print(f"✅ Конфигурация загружена: {config['database']}")
        return True
    except ImportError as e:
        print(f"❌ Не удалось импортировать DBConfig: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка в конфигурации: {e}")
        return False


def test_database_creation():
    """Тестирует создание базы данных и таблиц."""
    print("\n" + "=" * 50)
    print("Тестирование создания базы данных")
    print("=" * 50)

    try:
        from database.models import create_database, create_tables

        if create_database():
            create_tables()
            print("✅ База данных и таблицы созданы")
            return True
        else:
            print("❌ Ошибка при создании БД")
            return False
    except Exception as e:
        print(f"❌ Ошибка при создании БД: {e}")
        return False


def test_database_connection():
    """Тестирует подключение к базе данных."""
    print("\n" + "=" * 50)
    print("Тестирование подключения к БД")
    print("=" * 50)

    try:
        from database.utils import DatabaseUtils
        connection = DatabaseUtils.get_db_connection()
        if connection:
            # Проверяем, что таблицы существуют
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            print(f"✅ Подключение к БД успешно")
            print(f"✅ Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")

            connection.close()
            return True
        else:
            print("❌ Не удалось подключиться к БД")
            return False
    except Exception as e:
        print(f"❌ Ошибка при подключении к БД: {e}")
        return False


def test_file_structure():
    """Проверяет структуру файлов проекта."""
    print("\n" + "=" * 50)
    print("Проверка структуры проекта")
    print("=" * 50)

    required_files = [
        "api/__init__.py",
        "api/hh_api.py",
        "database/__init__.py",
        "database/config.py",
        "database/models.py",
        "database/utils.py",
        ".env",
        "requirements.txt"
    ]

    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - ОТСУТСТВУЕТ")
            all_ok = False

    return all_ok


def main():
    """Основная функция тестирования."""
    print("=" * 60)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ ПРОЕКТА")
    print("=" * 60)

    # Исправлено: инициализация списка одним выражением
    test_results = [
        ("Структура проекта", test_file_structure()),
        ("Конфигурация БД", test_database_config()),
        ("Создание БД", test_database_creation()),
        ("Подключение к БД", test_database_connection())
    ]

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, test_success in test_results:
        status = "✅ ПРОЙДЕН" if test_success else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if test_success:
            passed += 1

    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Провалено: {total - passed}")

    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Можно переходить к созданию db_manager.py")
        return True
    else:
        print("\n⚠️  Есть проблемы, которые нужно исправить")
        return False


if __name__ == "__main__":
    all_passed = main()
    sys.exit(0 if all_passed else 1)