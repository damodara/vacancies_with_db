from typing import Any

import psycopg2

from config import config


class DBManager:
    """Класс для управления взаимодействием с базой данных PostgreSQL."""

    def __init__(self):
        """Конструктор класса, инициализирует поля класса."""
        self.db = None

    def create_db(
        self, loaded_vacancies: list, database_name: str, params: dict[str, Any]
    ) -> None:
        """
        Создает новую базу данных и наполняет её информацией о компаниях и вакансиях.
        Аргументы:
          - loaded_vacancies (list): Список загруженных вакансий.
          - database_name (str): Имя создаваемой базы данных.
          - params (dict): Параметры подключения к серверу PostgreSQL.
        """
        # Удаляем существующую базу данных, если она имеется
        conn = psycopg2.connect(dbname="postgres", **params)
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"DROP DATABASE IF EXISTS {database_name};")
        except psycopg2.DatabaseError as err:
            print(f"Ошибка удаления базы данных: {err}")
        finally:
            cur.close()
            conn.close()

        # Создаем новую базу данных
        conn = psycopg2.connect(dbname="postgres", **params)
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"CREATE DATABASE {database_name};")
            print(f"База данных {database_name} успешно создана.")
        except psycopg2.DatabaseError as err:
            print(f"Ошибка создания базы данных: {err}")
        finally:
            cur.close()
            conn.close()

        # Создаем таблицы в новой базе данных
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            # Таблица компаний
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    companies_id SERIAL PRIMARY KEY,
                    title VARCHAR(255) UNIQUE
                );
            """
            )

            # Таблица вакансий
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancies_id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES companies(companies_id),
                    title VARCHAR(255),
                    description VARCHAR,
                    salary FLOAT,
                    url VARCHAR UNIQUE
                );
            """
            )

            # Заполняем таблицы данными
            for company_data in loaded_vacancies:
                company_title = company_data["employer"]["name"]

                # Проверяем, существует ли компания
                cur.execute(
                    "SELECT companies_id FROM companies WHERE title=%s;",
                    (company_title,),
                )
                existing_company = cur.fetchone()

                if existing_company:
                    company_id = existing_company[0]
                else:
                    cur.execute(
                        "INSERT INTO companies(title) VALUES(%s) RETURNING companies_id;",
                        (company_title,),
                    )
                    company_id = cur.fetchone()[0]

                # Данные о вакансиях
                role = (
                    company_data["professional_roles"][0]["name"]
                    if company_data["professional_roles"]
                    else ""
                )
                vacancy_title = role or company_data["name"]
                description = (
                    company_data["snippet"]["responsibility"]
                    if company_data["snippet"]
                    else ""
                )
                salary = (
                    company_data["salary"]["from"] if company_data["salary"] else None
                )
                url = company_data["alternate_url"]

                # Проверяем, существует ли вакансия по URL
                cur.execute("SELECT vacancies_id FROM vacancies WHERE url=%s;", (url,))
                existing_vacancy = cur.fetchone()

                if not existing_vacancy:
                    # Вакансия ещё не существует, добавляем её
                    cur.execute(
                        """
                        INSERT INTO vacancies(company_id, title, description, salary, url)
                        VALUES (%s, %s, %s, %s, %s);
                    """,
                        (company_id, vacancy_title, description, salary, url),
                    )

        conn.commit()
        conn.close()

    def get_companies_and_vacancies_count(self, database_name: str) -> None:
        """
        Возвращает список всех компаний и количество вакансий у каждой компании.
        Аргумент:
          - database_name (str): Название базы данных.
        """
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.title, COUNT(vacancies.vacancies_id) AS vacancies_count
                FROM companies
                LEFT JOIN vacancies ON companies.companies_id = vacancies.company_id
                GROUP BY companies.companies_id;
            """
            )
            results = cur.fetchall()

        print("\nСписок компаний и количество вакансий:")
        for idx, row in enumerate(results, start=1):
            print(f"{idx}. Компания: {row[0]} - Количество вакансий: {row[1]}")
        conn.close()

    def get_all_vacancies(self, database_name: str) -> None:
        """
        Возвращает список всех вакансий с названием компании, вакансии, зарплаты и ссылкой на вакансию.
        Аргумент:
          - database_name (str): Название базы данных.
        """
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.title AS company_name,
                       vacancies.title AS job_title,
                       vacancies.salary AS salary,
                       vacancies.url AS vacancy_link
                FROM vacancies
                INNER JOIN companies ON vacancies.company_id = companies.companies_id;
            """
            )
            results = cur.fetchall()

        print("\nСписок вакансий:")
        for idx, row in enumerate(results, start=1):
            print(
                f"{idx}. Компания: {row[0]} - Вакансия: {row[1]} - Зарплата от: {row[2]}, URL: {row[3]}"
            )
        conn.close()

    def get_avg_salary(self, database_name: str) -> None:
        """
        Возвращает среднюю зарплату по всем вакансиям.
        Аргумент:
          - database_name (str): Название базы данных.
        """
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("SELECT AVG(salary) FROM vacancies;")
            avg_salary = round(cur.fetchone()[0])

        print(f"\nСредняя зарплата: {avg_salary} рублей.")
        conn.close()

    def get_vacancies_with_higher_salary(self, database_name: str) -> None:
        """
        Возвращает список вакансий с зарплатой выше средней.
        Аргумент:
          - database_name (str): Название базы данных.
        """
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT title, salary
                FROM vacancies
                WHERE salary > (SELECT AVG(salary) FROM vacancies)
                ORDER BY salary ASC;
            """
            )
            results = cur.fetchall()

        print("\nВакансии с зарплатой выше средней:")
        for idx, row in enumerate(results, start=1):
            print(f"{idx}. Вакансия: {row[0]} - Зарплата от: {row[1]}")
        conn.close()

    def get_vacancies_with_keyword(self, database_name: str, keyword: str) -> None:
        """
        Возвращает список вакансий, содержащих указанный ключ в описании.
        Аргументы:
          - database_name (str): Название базы данных.
          - keyword (str): Ключ для поиска.
        """
        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            query = """
                SELECT companies.title AS company_name,
                       vacancies.title AS job_title,
                       vacancies.description,
                       vacancies.salary AS salary,
                       vacancies.url AS vacancy_link
                FROM vacancies
                INNER JOIN companies ON vacancies.company_id = companies.companies_id
                WHERE vacancies.description ILIKE %s;
            """
            cur.execute(query, ("%" + keyword.lower() + "%",))
            results = cur.fetchall()

        if not results:
            print("Нет вакансий, соответствующих вашему запросу.")
        else:
            print(f"\nСписок вакансий, в описании которых есть слово '{keyword}':")
            for idx, row in enumerate(results, start=1):
                print(
                    f"{idx}. Компания: {row[0]} - Вакансия: {row[1]} - Описание: {row[2]} - Зарплата от: {row[3]}, URL: {row[4]}"
                )
        conn.close()
