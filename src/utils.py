from typing import Any

import psycopg2
class DBManager:
    """Класс для подключения к БД PostgreSQL"""
    def __init__(self):
        self.db = None

    def get_companies_and_vacancies_count(self, loaded_vacancies:  list[dict[str, Any]]):
        """получает список всех компаний и количество вакансий у каждой компании"""
        all_companies_name = set()
        all_companies_count: int
        for vacancy in loaded_vacancies:
            company_name = vacancy['employer']['name']
            all_companies_name.add(company_name)

        print(f"Список всех компаний: {all_companies_name}")
        all_companies_count = len(all_companies_name)
        print(f"Количество всех компаний: {all_companies_count}")



    def get_all_vacancies(self, loaded_vacancies:  list[dict[str, Any]]):
        """получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на
        вакансию."""
        list_vacancies = []

        for vacancy in loaded_vacancies:
            company_name = vacancy['employer']['name']
            vacancy_name = vacancy['name']
            salary = vacancy['salary'].get('from') if vacancy.get('salary') else None
            link = vacancy['alternate_url']

            list_vacancies.append({
                'company': company_name,
                'job_title': vacancy_name,
                'salary': salary,
                'link': link
            })

        # Красивый вывод списка вакансий
        print("\nСписок вакансий:")
        for idx, vacancy_data in enumerate(list_vacancies, start=1):
            print(
                f"{idx}. {vacancy_data['job_title']} ({vacancy_data['company']}) - Зарплата: {vacancy_data['salary']}, ссылка: {vacancy_data['link']}")




    def get_avg_salary(self, loaded_vacancies:  list[dict[str, Any]]):
        """получает среднюю зарплату по вакансиям."""



    def get_vacancies_with_higher_salary(self, loaded_vacancies:  list[dict[str, Any]]):
        """получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        pass

    def get_vacancies_with_keyword(self, loaded_vacancies:  list[dict[str, Any]]):
        """получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""
        pass