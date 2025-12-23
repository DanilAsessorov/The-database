import requests
from typing import Dict, List, Optional
import time
import sys
import os

# Добавляем корень проекта в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HeadHunterAPI:
    """Класс для работы с API hh.ru."""

    def __init__(self):
        self.base_url = "https://api.hh.ru"

    def get_employer_info(self, employer_id: str) -> Optional[Dict]:
        """Получает информацию о компании."""
        url = f"{self.base_url}/employers/{employer_id}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при получении компании {employer_id}: {e}")
            return None

    def get_employer_vacancies(self, employer_id: str, employer_name: str = "") -> List[Dict]:
        """Получает все вакансии компании."""
        url = f"{self.base_url}/vacancies"
        all_vacancies = []
        page = 0
        pages = 1

        print(f"📥 Получаем вакансии: {employer_name or employer_id}")

        while page < pages:
            params = {
                "employer_id": employer_id,
                "per_page": 100,
                "page": page,
                "only_with_salary": True
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                vacancies = data.get("items", [])
                all_vacancies.extend(vacancies)

                pages = data.get("pages", 1)
                found = data.get("found", 0)

                print(f"  📄 Страница {page + 1}/{pages}, найдено: {found}")

                time.sleep(0.1)  # Пауза, чтобы не перегружать API
                page += 1

            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка на странице {page}: {e}")
                break

        print(f"  ✅ Получено вакансий: {len(all_vacancies)}")
        return all_vacancies


# Список компаний для сбора
COMPANIES = {
    "1740": "Яндекс",
    "3529": "Сбер",
    "15478": "VK",
    "2180": "Ozon",
    "78638": "Тинькофф",
    "80": "Авито",
    "4181": "1С",
    "3776": "МТС",
    "1057": "Касперский",
    "1455": "HeadHunter"
}


def collect_data_from_hh():
    """Собирает данные с hh.ru и сохраняет в базу."""
    api = HeadHunterAPI()

    print("=" * 60)
    print("СБОР ДАННЫХ С HH.RU")
    print("=" * 60)

    all_employers_data = []
    all_vacancies_data = []

    # Собираем данные компаний
    print("\n📊 Получаем данные компаний:")
    for employer_id, employer_name in COMPANIES.items():
        print(f"\n🏢 {employer_name} (ID: {employer_id})")

        employer_info = api.get_employer_info(employer_id)
        if employer_info:
            employer_data = {
                "hh_id": employer_id,
                "name": employer_info.get("name", employer_name),
                "url": employer_info.get("site_url", ""),
                "description": employer_info.get("description", "")[:500],
                "open_vacancies": employer_info.get("open_vacancies", 0)
            }
            all_employers_data.append(employer_data)
            print(f"  ✅ Данные компании получены")
        else:
            print(f"  ❌ Не удалось получить данные компании")

    # Сохраняем компании в БД
    try:
        from database.utils import DatabaseUtils
        if all_employers_data:
            DatabaseUtils.save_employers_to_db(all_employers_data)

        # Получаем employer_id из БД для связи
        employer_mapping = DatabaseUtils.get_employer_mapping()

        # Собираем вакансии
        print("\n📋 Получаем вакансии компаний:")
        for employer_id, employer_name in COMPANIES.items():
            vacancies = api.get_employer_vacancies(employer_id, employer_name)
            all_vacancies_data.extend(vacancies)

        # Сохраняем вакансии в БД
        if all_vacancies_data:
            DatabaseUtils.save_vacancies_to_db(all_vacancies_data, employer_mapping)

        print("\n" + "=" * 60)
        print("📊 ИТОГИ СБОРА ДАННЫХ:")
        print(f"✅ Компаний собрано: {len(all_employers_data)}")
        print(f"✅ Вакансий собрано: {len(all_vacancies_data)}")
        print("=" * 60)

        return len(all_employers_data), len(all_vacancies_data)

    except ImportError:
        print("❌ Не удалось импортировать DatabaseUtils")
        print("   Убедитесь, что файл database/utils.py существует")
        return 0, 0
    except Exception as e:
        print(f"❌ Ошибка при сохранении в БД: {e}")
        return 0, 0


if __name__ == "__main__":
    collect_data_from_hh()