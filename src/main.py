import os
import sys
from typing import Any, Callable, NoReturn, Optional

# Добавляем родительскую папку в путь для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Определяем переменные с типами и значениями по умолчанию ДО try-блока
DBManager: Optional[type] = None
initialize_database_func: Optional[Callable[[], bool]] = None
clear_tables_func: Optional[Callable[[], bool]] = None
collect_data_from_hh_func: Optional[Callable[[], tuple[int, int]]] = None

try:
    from api.hh_api import collect_data_from_hh as imported_collect_hh
    from database.db_manager import DBManager as ImportedDBManager
    from database.models import clear_tables as imported_clear_tables
    from database.models import initialize_database as imported_init_db

    # Присваиваем импортированные значения
    DBManager = ImportedDBManager
    initialize_database_func = imported_init_db
    clear_tables_func = imported_clear_tables
    collect_data_from_hh_func = imported_collect_hh

except ImportError as import_error:
    print(f"❌ Ошибка импорта модулей: {import_error}")
    print("\n📁 Проверьте структуру проекта:")
    print("   PythonProject2/")
    print("   ├── api/hh_api.py")
    print("   ├── database/")
    print("   │   ├── config.py")
    print("   │   ├── db_manager.py")
    print("   │   ├── models.py")
    print("   │   └── utils.py")
    print("   ├── src/main.py (этот файл)")
    print("   └── requirements.txt")
    sys.exit(1)


def display_companies_and_vacancies(db_instance: Any) -> None:
    """Показывает компании и количество вакансий."""
    print("\n" + "=" * 60)
    print("КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 60)

    try:
        companies = db_instance.get_companies_and_vacancies_count()
        if companies:
            for company, count in companies:
                print(f"🏢 {company}: {count} вакансий")
        else:
            print("📭 Нет данных о компаниях в базе")
    except AttributeError as attr_error:
        print(f"❌ Ошибка метода: {attr_error}")
    except Exception as display_error:  # pylint: disable=broad-except
        print(f"❌ Ошибка при получении данных: {display_error}")


def display_all_vacancies(db_instance: Any) -> None:
    """Показывает все вакансии."""
    print("\n" + "=" * 60)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 60)

    try:
        vacancies = db_instance.get_all_vacancies()
        if vacancies:
            print(f"📊 Найдено вакансий: {len(vacancies)}")
            for idx, (company, title, salary_from, salary_to, currency, url) in enumerate(vacancies, 1):
                salary_str = "з/п не указана"
                if salary_from or salary_to:
                    if salary_from and salary_to:
                        salary_str = f"{salary_from:,} - {salary_to:,} {currency or 'руб.'}"
                    elif salary_from:
                        salary_str = f"от {salary_from:,} {currency or 'руб.'}"
                    else:
                        salary_str = f"до {salary_to:,} {currency or 'руб.'}"

                print(f"\n{idx}. 🏢 {company}")
                print(f"   💼 {title}")
                print(f"   💰 {salary_str}")
                print(f"   🔗 {url}")

                # Пауза после каждых 10 вакансий
                if idx % 10 == 0 and idx < len(vacancies):
                    try:
                        input("\n⏎ Показать еще (Enter)...")
                        print("-" * 40)
                    except (KeyboardInterrupt, EOFError):
                        print("\n⏹️  Показать прервано")
                        break
        else:
            print("📭 Нет вакансий в базе данных")
    except AttributeError as attr_error:
        print(f"❌ Ошибка метода: {attr_error}")
    except Exception as display_error:  # pylint: disable=broad-except
        print(f"❌ Ошибка при получении вакансий: {display_error}")


def display_vacancies_by_keyword(db_instance: Any) -> None:
    """Ищет вакансии по ключевому слову."""
    try:
        keyword = input("\n🔍 Введите ключевое слово для поиска: ").strip()
        if not keyword:
            print("⚠️  Ключевое слово не введено")
            return

        print(f"\n" + "=" * 60)
        print(f"ПОИСК ВАКАНСИЙ: '{keyword}'")
        print("=" * 60)

        vacancies = db_instance.get_vacancies_with_keyword(keyword)
        if vacancies:
            print(f"✅ Найдено вакансий: {len(vacancies)}")
            for idx, (company, title, salary_from, salary_to, currency, url) in enumerate(vacancies, 1):
                salary_str = "з/п не указана"
                if salary_from or salary_to:
                    if salary_from and salary_to:
                        salary_str = f"{salary_from:,} - {salary_to:,} {currency or 'руб.'}"
                    elif salary_from:
                        salary_str = f"от {salary_from:,} {currency or 'руб.'}"
                    else:
                        salary_str = f"до {salary_to:,} {currency or 'руб.'}"

                print(f"\n{idx}. 🏢 {company}")
                print(f"   💼 {title}")
                print(f"   💰 {salary_str}")
                print(f"   🔗 {url}")
        else:
            print(f"📭 Вакансий по запросу '{keyword}' не найдено")
    except (KeyboardInterrupt, EOFError):
        print("\n⏹️  Поиск прерван")
    except AttributeError as attr_error:
        print(f"❌ Ошибка метода: {attr_error}")
    except Exception as search_error:  # pylint: disable=broad-except
        print(f"❌ Ошибка при поиске: {search_error}")


def display_statistics(db_instance: Any) -> None:
    """Показывает статистику."""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА")
    print("=" * 60)

    try:
        employers_count = db_instance.get_employers_count()
        vacancies_count = db_instance.get_vacancies_count()
        avg_salary = db_instance.get_avg_salary()
        high_salary_vacancies = db_instance.get_vacancies_with_higher_salary()
        high_salary_count = len(high_salary_vacancies)

        print(f"📊 КОМПАНИИ: {employers_count}")
        print(f"📊 ВАКАНСИИ: {vacancies_count}")

        if vacancies_count > 0:
            print(f"💰 СРЕДНЯЯ ЗАРПЛАТА: {avg_salary:,.2f} руб.")
            print(f"📈 ВАКАНСИЙ С З/П ВЫШЕ СРЕДНЕЙ: {high_salary_count}")

            percentage = (high_salary_count / vacancies_count) * 100
            print(f"📊 ПРОЦЕНТ ВЫСОКООПЛАЧИВАЕМЫХ: {percentage:.1f}%")

            # Показываем топ-5 высокооплачиваемых вакансий
            if high_salary_vacancies:
                print(f"\n🏆 ТОП-5 высокооплачиваемых вакансий:")
                for i, (company, title, salary_from, salary_to, currency, url) in enumerate(
                    high_salary_vacancies[:5], 1
                ):
                    salary_avg = (
                        (salary_from + salary_to) / 2 if salary_from and salary_to else salary_from or salary_to or 0
                    )
                    print(f"{i}. {company} - {title} ({salary_avg:,.0f} руб.)")
        else:
            print("📭 В базе нет данных о вакансиях")

    except AttributeError as attr_error:
        print(f"❌ Ошибка метода: {attr_error}")
    except Exception as stats_error:  # pylint: disable=broad-except
        print(f"❌ Ошибка при получении статистики: {stats_error}")


def collect_data_menu(db_instance: Any) -> bool:
    """Собирает данные с hh.ru."""
    print("\n" + "=" * 60)
    print("СБОР ДАННЫХ С HH.RU")
    print("=" * 60)

    print("ℹ️  Будет собрана информация о 10 IT-компаниях:")
    print("   Яндекс, Сбер, VK, Ozon, Тинькофф,")
    print("   Авито, 1С, МТС, Касперский, HeadHunter")

    try:
        confirm = input("\n⚠️  Продолжить? (да/НЕТ): ").strip().lower()
        if confirm not in ["да", "д", "yes", "y"]:
            print("⏹️  Сбор данных отменен")
            return False
    except (KeyboardInterrupt, EOFError):
        print("\n⏹️  Сбор данных отменен")
        return False

    print("\n⏳ Сбор данных может занять 2-5 минут...")

    try:
        if not collect_data_from_hh_func:
            print("❌ Функция сбора данных не найдена")
            return False

        companies, vacancies = collect_data_from_hh_func()

        if companies > 0 and vacancies > 0:
            print(f"\n✅ УСПЕШНО СОБРАНО:")
            print(f"   🏢 Компаний: {companies}")
            print(f"   💼 Вакансий: {vacancies}")

            # Обновляем статистику
            print(f"\n📊 ОБНОВЛЕННАЯ СТАТИСТИКА:")
            print(f"   Всего компаний: {db_instance.get_employers_count()}")
            print(f"   Всего вакансий: {db_instance.get_vacancies_count()}")
            return True
        else:
            print("\n❌ Не удалось собрать данные")
            print("   Возможные причины:")
            print("   1. Нет подключения к интернету")
            print("   2. API HH.ru недоступно")
            print("   3. Ошибка при сохранении в базу данных")
            return False

    except AttributeError as attr_error:
        print(f"❌ Ошибка метода: {attr_error}")
        return False
    except Exception as collect_error:  # pylint: disable=broad-except
        print(f"❌ Ошибка при сборе данных: {collect_error}")
        return False


def confirm_clear_database() -> bool:
    """Запрашивает подтверждение очистки базы данных."""
    print("\n" + "=" * 60)
    print("⚠️  ОЧИСТКА БАЗЫ ДАННЫХ")
    print("=" * 60)
    print("❌ ВНИМАНИЕ: Все данные будут удалены безвозвратно!")

    try:
        confirm = input("\nВы уверены? (введите 'УДАЛИТЬ' для подтверждения): ").strip()
        if confirm == "УДАЛИТЬ":
            return True
        else:
            print("⏹️  Очистка отменена")
            return False
    except (KeyboardInterrupt, EOFError):
        print("\n⏹️  Очистка отменена")
        return False


def main_menu() -> None:
    """Главное меню программы."""
    print("\n" + "=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)

    # Проверяем доступность функции инициализации
    if not initialize_database_func:
        print("❌ Функция инициализации базы данных не найдена")
        return

    # Инициализируем базу данных PostgreSQL
    if not initialize_database_func():
        print("\n❌ НЕ УДАЛОСЬ ИНИЦИАЛИЗИРОВАТЬ БАЗУ ДАННЫХ")
        print("   Проверьте:")
        print("   1. Установлен ли PostgreSQL")
        print("   2. Настройки в файле .env")
        print("   3. Доступность сервера PostgreSQL")
        print("   4. Правильность логина и пароля")
        return

    # Проверяем доступность DBManager
    if DBManager is None:
        print("❌ Класс DBManager не найден")
        return

    # Создаем менеджер БД
    db_instance = DBManager()

    while True:
        print("\n" + "=" * 60)
        print("АНАЛИЗ ВАКАНСИЙ С HH.RU")
        print("=" * 60)

        # Показываем текущую статистику
        try:
            employers = db_instance.get_employers_count()
            vacancies = db_instance.get_vacancies_count()
            print(f"📊 ТЕКУЩАЯ СТАТИСТИКА: {employers} компаний, {vacancies} вакансий")
        except AttributeError:
            print("📊 ТЕКУЩАЯ СТАТИСТИКА: методы не найдены")
        except Exception:  # pylint: disable=broad-except
            print("📊 ТЕКУЩАЯ СТАТИСТИКА: ошибка при получении")

        print("=" * 60)

        print("1. 📊 Показать компании и количество вакансий")
        print("2. 📋 Показать все вакансии")
        print("3. 🔍 Найти вакансии по ключевому слову")
        print("4. 📈 Показать статистику")
        print("5. 📥 Собрать данные с hh.ru")
        print("6. 🗑️  Очистить базу данных")
        print("7. ℹ️  О программе")
        print("8. 🚪 Выход")
        print("=" * 60)

        try:
            choice = input("\n🎯 Выберите действие (1-8): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Программа завершена")
            break

        if choice == "1":
            display_companies_and_vacancies(db_instance)
        elif choice == "2":
            display_all_vacancies(db_instance)
        elif choice == "3":
            display_vacancies_by_keyword(db_instance)
        elif choice == "4":
            display_statistics(db_instance)
        elif choice == "5":
            collect_data_menu(db_instance)
        elif choice == "6":
            if confirm_clear_database():
                if clear_tables_func and clear_tables_func():
                    print("✅ База данных очищена")
                else:
                    print("❌ Функция очистки не доступна")
        elif choice == "7":
            print("\n" + "=" * 60)
            print("О ПРОГРАММЕ")
            print("=" * 60)
            print("Парсер вакансий HH.ru с PostgreSQL")
            print("Версия: 1.0")
            print("\nВозможности:")
            print("• Сбор данных о компаниях с HH.ru")
            print("• Сбор вакансий с указанием зарплат")
            print("• Поиск вакансий по ключевым словам")
            print("• Статистика по вакансиям")
            print("• Хранение данных в PostgreSQL")
        elif choice == "8":
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Введите число от 1 до 8.")

        if choice not in ["7", "8"]:
            try:
                input("\n⏎ Нажмите Enter для продолжения...")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Программа завершена")
                break


def main() -> NoReturn:
    """Главная функция приложения."""
    try:
        print("=" * 60)
        print("ПАРСЕР ВАКАНСИЙ HH.RU С POSTGRESQL")
        print("=" * 60)

        main_menu()

    except KeyboardInterrupt:
        print("\n\n⏹️  Программа прервана пользователем")
        sys.exit(0)
    except ImportError as import_error:
        print(f"\n❌ ОШИБКА ИМПОРТА: {import_error}")
        print("\n🔧 Установите зависимости: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as main_error:  # pylint: disable=broad-except
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {main_error}")
        print("\n🔧 ДЕЙСТВИЯ ПО УСТРАНЕНИЮ:")
        print("   1. Проверьте файл .env с настройками")
        print("   2. Убедитесь, что установлены все зависимости")
        print("   3. Проверьте, запущен ли сервер PostgreSQL")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n" + "=" * 60)
        print("ПРОГРАММА ЗАВЕРШЕНА")
        print("=" * 60)


if __name__ == "__main__":
    main()
