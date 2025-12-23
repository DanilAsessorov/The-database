import sys
import os

# Добавляем корень проекта в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DBManager


def display_companies_and_vacancies(db: DBManager):
    """Показывает компании и количество вакансий."""
    print("\n" + "=" * 60)
    print("КОМПАНИИ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * 60)

    companies = db.get_companies_and_vacancies_count()
    if companies:
        for company, count in companies:
            print(f"🏢 {company}: {count} вакансий")
    else:
        print("Нет данных о компаниях")


def display_all_vacancies(db: DBManager):
    """Показывает все вакансии."""
    print("\n" + "=" * 60)
    print("ВСЕ ВАКАНСИИ")
    print("=" * 60)

    vacancies = db.get_all_vacancies()
    if vacancies:
        for company, title, salary_from, salary_to, currency, url in vacancies:
            if salary_from or salary_to:
                if salary_from and salary_to:
                    salary = f"{salary_from:,} - {salary_to:,} {currency}"
                elif salary_from:
                    salary = f"от {salary_from:,} {currency}"
                else:
                    salary = f"до {salary_to:,} {currency}"
            else:
                salary = "з/п не указана"

            print(f"\n🏢 {company}")
            print(f"💼 {title}")
            print(f"💰 {salary}")
            print(f"🔗 {url}")
            print("-" * 40)
    else:
        print("Нет вакансий")


def display_vacancies_by_keyword(db: DBManager):
    """Ищет вакансии по ключевому слову."""
    keyword = input("\nВведите ключевое слово для поиска: ").strip()
    if not keyword:
        print("❌ Ключевое слово не введено")
        return

    print(f"\n" + "=" * 60)
    print(f"ВАКАНСИИ ПО ЗАПРОСУ: '{keyword}'")
    print("=" * 60)

    vacancies = db.get_vacancies_with_keyword(keyword)
    if vacancies:
        for company, title, salary_from, salary_to, currency, url in vacancies:
            if salary_from or salary_to:
                if salary_from and salary_to:
                    salary = f"{salary_from:,} - {salary_to:,} {currency}"
                elif salary_from:
                    salary = f"от {salary_from:,} {currency}"
                else:
                    salary = f"до {salary_to:,} {currency}"
            else:
                salary = "з/п не указана"

            print(f"\n🏢 {company}")
            print(f"💼 {title}")
            print(f"💰 {salary}")
            print(f"🔗 {url}")
    else:
        print(f"Вакансий по запросу '{keyword}' не найдено")


def display_statistics(db: DBManager):
    """Показывает статистику."""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА")
    print("=" * 60)

    avg_salary = db.get_avg_salary()
    print(f"💰 Средняя зарплата: {avg_salary:,.2f} руб.")

    high_salary_vacancies = db.get_vacancies_with_higher_salary()
    print(f"📈 Вакансий с зарплатой выше средней: {len(high_salary_vacancies)}")


def collect_data_from_hh():
    """Собирает данные с hh.ru."""
    try:
        from api.hh_api import collect_data_from_hh as hh_collector
        print("\n⚠️  Сбор данных может занять несколько минут...")
        companies, vacancies = hh_collector()
        print(f"\n✅ Собрано: {companies} компаний, {vacancies} вакансий")
        return True
    except ImportError:
        print("❌ Модуль api.hh_api не найден")
        print("   Создайте файл api/hh_api.py с кодом для работы с api hh.ru")
        return False
    except Exception as e:
        print(f"❌ Ошибка при сборе данных: {e}")
        return False


def main_menu():
    """Главное меню программы."""
    db = DBManager()

    while True:
        print("\n" + "=" * 60)
        print("АНАЛИЗ ВАКАНСИЙ С HH.RU")
        print("=" * 60)
        print("1. 📊 Показать компании и количество вакансий")
        print("2. 📋 Показать все вакансии")
        print("3. 🔍 Найти вакансии по ключевому слову")
        print("4. 📈 Показать статистику")
        print("5. 📥 Собрать данные с hh.ru (заполнить БД)")
        print("6. 🚪 Выход")
        print("=" * 60)

        try:
            choice = input("Выберите действие (1-6): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Программа завершена")
            break

        if choice == "1":
            display_companies_and_vacancies(db)
        elif choice == "2":
            display_all_vacancies(db)
        elif choice == "3":
            display_vacancies_by_keyword(db)
        elif choice == "4":
            display_statistics(db)
        elif choice == "5":
            collect_data_from_hh()
        elif choice == "6":
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

        try:
            input("\nНажмите Enter для продолжения...")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Программа завершена")
            break


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"\n❌ Произошла непредвиденная ошибка: {e}")
        print("Проверьте, что все модули установлены и настроены правильно.")