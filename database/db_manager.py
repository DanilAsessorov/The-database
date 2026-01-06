from typing import List, Optional, Tuple

import psycopg

from database.config import DBConfig


class DBManager:
    """
    Класс для работы с базой данных PostgreSQL.
    Реализует все требуемые методы по заданию.
    """

    def __init__(self):
        """
        Инициализация менеджера БД.
        Использует конфигурацию из DBConfig.
        """
        self.config = DBConfig.get_db_config()

    def _get_connection(self) -> psycopg.Connection:
        """Возвращает соединение с базой данных PostgreSQL."""
        return psycopg.connect(**self.config)

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT e.name, COUNT(v.vacancy_id) as vacancy_count
                    FROM employers e
                    LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                    GROUP BY e.employer_id, e.name
                    ORDER BY vacancy_count DESC
                """
                )
                return cursor.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает список всех вакансий.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
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
                """
                )
                return cursor.fetchall()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT AVG(
                        CASE
                            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                            THEN (salary_from + salary_to) / 2.0
                            WHEN salary_from IS NOT NULL THEN salary_from::float
                            WHEN salary_to IS NOT NULL THEN salary_to::float
                            ELSE NULL
                        END
                    ) as avg_salary
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                """
                )
                result = cursor.fetchone()
                return round(float(result[0] or 0), 2) if result else 0.0

    def get_vacancies_with_higher_salary(
        self,
    ) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает вакансии с зарплатой выше средней.
        """
        avg_salary = self.get_avg_salary()

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        e.name as company_name,
                        v.title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE (
                        CASE
                            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                            THEN (salary_from + salary_to) / 2.0
                            WHEN salary_from IS NOT NULL THEN salary_from::float
                            WHEN salary_to IS NOT NULL THEN salary_to::float
                            ELSE 0
                        END
                    ) > %s
                    ORDER BY (
                        CASE
                            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                            THEN (salary_from + salary_to) / 2.0
                            WHEN salary_from IS NOT NULL THEN salary_from::float
                            WHEN salary_to IS NOT NULL THEN salary_to::float
                            ELSE 0
                        END
                    ) DESC
                """,
                    (avg_salary,),
                )
                return cursor.fetchall()

    def get_vacancies_with_keyword(
        self, keyword: str
    ) -> List[Tuple[str, str, Optional[int], Optional[int], Optional[str], str]]:
        """
        Получает вакансии по ключевому слову.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        e.name as company_name,
                        v.title,
                        v.salary_from,
                        v.salary_to,
                        v.currency,
                        v.url
                    FROM vacancies v
                    JOIN employers e ON v.employer_id = e.employer_id
                    WHERE v.title ILIKE %s
                    ORDER BY e.name, v.title
                """,
                    (f"%{keyword}%",),
                )
                return cursor.fetchall()

    def get_employers_count(self) -> int:
        """Количество компаний в БД."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM employers")
                return cursor.fetchone()[0]

    def get_vacancies_count(self) -> int:
        """Количество вакансий в БД."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM vacancies")
                return cursor.fetchone()[0]


def test_db_manager():
    """Тестирование методов DBManager."""
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ DBManager (PostgreSQL)")
    print("=" * 50)

    try:
        db = DBManager()

        print(f"✅ Компаний в БД: {db.get_employers_count()}")
        print(f"✅ Вакансий в БД: {db.get_vacancies_count()}")

        companies = db.get_companies_and_vacancies_count()
        print(f"✅ Компаний с вакансиями: {len(companies)}")

        vacancies = db.get_all_vacancies()
        print(f"✅ Всего вакансий: {len(vacancies)}")

        avg_salary = db.get_avg_salary()
        print(f"✅ Средняя зарплата: {avg_salary}")

        high_salary = db.get_vacancies_with_higher_salary()
        print(f"✅ Вакансий с з/п выше средней: {len(high_salary)}")

        python_vacancies = db.get_vacancies_with_keyword("python")
        print(f"✅ Вакансий с 'python': {len(python_vacancies)}")

        print("\n🎉 Все методы DBManager работают с PostgreSQL!")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    test_db_manager()
