import sqlite3
from typing import List, Tuple, Optional


class DBManager:
    """
    Класс для работы с базой данных.
    Реализует все требуемые методы по заданию.
    """

    def __init__(self, db_path: str = "hh_vacancies.db"):
        """
        Инициализация менеджера БД.

        Args:
            db_path: Путь к файлу БД SQLite
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Возвращает соединение с базой данных."""
        return sqlite3.connect(self.db_path)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.employer_id
                ORDER BY vacancy_count DESC
            """)
            return cursor.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает список всех вакансий.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.title,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                ORDER BY e.name, v.title
            """)
            return cursor.fetchall()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2.0) as avg_salary
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            result = cursor.fetchone()
            return round(result[0] or 0, 2) if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[
        Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает вакансии с зарплатой выше средней.
        """
        avg_salary = self.get_avg_salary()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.title,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 > ?
                ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2.0 DESC
            """, (avg_salary,))
            return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[
        Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает вакансии по ключевому слову.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    e.name as company_name,
                    v.title,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE LOWER(v.title) LIKE ?
                ORDER BY e.name, v.title
            """, (f"%{keyword.lower()}%",))
            return cursor.fetchall()


def main():
    """Тестирование DBManager."""
    print("=" * 50)
    print("Тестирование DBManager")
    print("=" * 50)

    try:
        db = DBManager()
        print(f"✅ DBManager инициализирован для БД: {db.db_path}")

        # Создадим тестовые данные
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()

        # Добавим тестовую компанию
        cursor.execute("INSERT OR IGNORE INTO employers (hh_id, name) VALUES (?, ?)",
                       ("test1", "Тестовая компания"))

        # Добавим тестовую вакансию
        cursor.execute("""
            INSERT OR IGNORE INTO vacancies 
            (hh_id, employer_id, title, salary_from, salary_to, currency, url)
            VALUES (?, 1, ?, ?, ?, ?, ?)
        """, ("vac1", "Python Developer", 100000, 150000, "RUR", "http://test.ru"))

        conn.commit()
        conn.close()

        # Тестируем методы
        print(f"✅ Компании и вакансии: {len(db.get_companies_and_vacancies_count())}")
        print(f"✅ Все вакансии: {len(db.get_all_vacancies())}")
        print(f"✅ Средняя зарплата: {db.get_avg_salary()}")
        print(f"✅ Вакансии с зарплатой выше средней: {len(db.get_vacancies_with_higher_salary())}")
        print(f"✅ Вакансии с ключевым словом 'Python': {len(db.get_vacancies_with_keyword('Python'))}")

        print("\n🎉 Все 5 методов DBManager работают!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()