from typing import Any
import psycopg2
from config import config


class DBManager:
    """Класс для подключения к БД PostgreSQL"""
    def __init__(self):
        self.db = None

    def create_db(self,loaded_vacancies,  database_name: str, params: dict[str, Any]) -> None:
        """Создание БД PostgreSQL"""
        conn = psycopg2.connect(dbname='postgres', **params)
        conn.autocommit = True
        cur = conn.cursor()

        try:
            # Попытка удалить старую базу данных
            cur.execute(f"DROP DATABASE IF EXISTS {database_name};")
        except psycopg2.DatabaseError as error:
            print(f"Ошибка при удалении старой базы данных: {error}")

        try:
            # Создание новой базы данных
            cur.execute(f"CREATE DATABASE {database_name};")
            print(f"Новая база данных {database_name} успешно создана.")
        except psycopg2.DatabaseError as error:
            print(f"Ошибка при создании базы данных: {error}")

        cur.close()
        conn.close()
        #Создание таблицы companies
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    companies_id SERIAL PRIMARY KEY,
                    title VARCHAR(255) UNIQUE 
                )
            """)
            print("Таблица companies создана")
        # Создание таблицы vacancies
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS vacancies
                        (
                            vacancies_id SERIAL PRIMARY KEY,
                            company_id   INT REFERENCES companies (companies_id),
                            title        VARCHAR(255),
                            description  VARCHAR,
                            salary       FLOAT,
                            url          VARCHAR UNIQUE -- Ограничиваем уникальностью поле url
                        )
                        """)
            print("Таблица vacancies создана")
        # Наполнение таблицы companies и vacancies
        with conn.cursor() as cur:
            for company in loaded_vacancies:
                company_title = company['employer']['name']

                # Проверяем существование компании
                cur.execute("""
                            SELECT companies_id
                            FROM companies
                            WHERE title = %s
                            """, (company_title,))
                existing_company = cur.fetchone()

                if existing_company:
                    company_id = existing_company[0]
                else:
                    cur.execute("""
                                INSERT INTO companies (title)
                                VALUES (%s)
                                RETURNING companies_id
                                """, (company_title,))
                    company_id = cur.fetchone()[0]

                # Данные о вакансиях
                first_role = company['professional_roles'][0]
                vacancies_title = first_role['name']
                description = company['snippet']['responsibility']
                salary = company['salary']['from'] if company['salary'] else None
                url = company['alternate_url']

                # Проверяем существование вакансии по URL
                cur.execute("""
                            SELECT vacancies_id
                            FROM vacancies
                            WHERE url = %s
                            """, (url,))
                existing_vacancy = cur.fetchone()

                if not existing_vacancy:
                    # Вакансия ещё не существует, добавляем её
                    cur.execute("""
                                INSERT INTO vacancies (company_id, title, description, salary, url)
                                VALUES (%s, %s, %s, %s, %s)
                                """, (company_id, vacancies_title, description, salary, url))

        conn.commit()
        conn.close()

    def get_companies_and_vacancies_count(self, database_name: str) -> None:
        """Получает список всех компаний и количество вакансий у каждой компании из базы данных"""
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            # Запрашиваем компании и количество вакансий
            cur.execute("""
                SELECT companies.title, COUNT(vacancies.vacancies_id) AS vacancies_count
                FROM companies
                LEFT JOIN vacancies ON companies.companies_id = vacancies.company_id
                GROUP BY companies.companies_id
            """)
            results = cur.fetchall()
            print(results)
        # Вывод результата
        print("\nСписок компаний и количество вакансий:")
        for row in results:
            print(f" - {row[0]} - Количество вакансий: {row[1]}")

        conn.close()


    def get_all_vacancies(self, loaded_vacancies:  list[dict[str, Any]], database_name: str) -> None:
        """получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на
        вакансию."""
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            for company in loaded_vacancies:
                company_title = company['employer']['name']
                description = company['snippet']['responsibility']
                salary = company['salary']['from'] if company['salary'] else None
                url = company['alternate_url']
                cur.execute("""
                SELECT vacancies_id
                FROM vacancies
                    
            """)
                existing_vacancy = cur.fetchone()


        # list_vacancies = []
        #
        # for vacancy in loaded_vacancies:
        #     company_name = vacancy['employer']['name']
        #     vacancy_name = vacancy['name']
        #     salary = vacancy['salary'].get('from') if vacancy.get('salary') else None
        #     link = vacancy['alternate_url']
        #
        #     list_vacancies.append({
        #         'company': company_name,
        #         'job_title': vacancy_name,
        #         'salary': salary,
        #         'link': link
        #     })
        #
        # # Красивый вывод списка вакансий
        # print("\nСписок вакансий:")
        # for idx, vacancy_data in enumerate(list_vacancies, start=1):
        #     print(
        #         f"{idx}. {vacancy_data['job_title']} ({vacancy_data['company']}) - Зарплата: {vacancy_data['salary']}, ссылка: {vacancy_data['link']}")




    def get_avg_salary(self, loaded_vacancies:  list[dict[str, Any]], database_name: str) -> None:
        """получает среднюю зарплату по вакансиям."""
        total_salary = 0
        count = 0
        for vacancy in loaded_vacancies:
            salary = vacancy['salary'].get('from')
            if salary:
                total_salary += salary
                count += 1
        avg_salary = total_salary / count
        rounded_salary = round(avg_salary, 2)
        print(f"Среднаяя зарплата: {rounded_salary} руб.")



    def get_vacancies_with_higher_salary(self, loaded_vacancies:  list[dict[str, Any]], database_name: str) -> None:
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        pass

    def get_vacancies_with_keyword(self, loaded_vacancies:  list[dict[str, Any]], database_name: str) -> None:
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""
        pass