from config import config
from src.api_connector import HeadHunterAPI
from src.utils import DBManager


def main():
    employer_ids = [
        "1907894",  # 1 red
        "1171877",  # globus
        "11545313",  # 3 Солюшен
        "9152217",  # 4 Код Грин Инжиниринг
        "1122462",  # 5 skyENG
        "45124",  # 6 Zecurion
        "4138182",  # 7 Topface Media
        "1911403",  # 8 Angara Security
        "4888751",  # 9 Рекруто
        "5591530",  # 10 IT-hunters
    ]

    # Создаем объект API
    hh_api = HeadHunterAPI()
    # Получаем вакансии
    loaded_vacancies = hh_api.get_vacancies(employer_ids)
    db_manager = DBManager()
    params = config()

    db_manager.create_db(loaded_vacancies, "headhunter", params)
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить список всех компаний и количество вакансий у каждой компании")
    print(
        "2. Получить список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию"
    )
    print("3. Получить среднюю зарплату по вакансиям")
    print(
        "4. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям"
    )
    print(
        "5. Получить список всех вакансий, в названии которых содержатся переданные в метод слова"
    )
    source = input().strip()
    if source == "1":
        db_manager.get_companies_and_vacancies_count("headhunter")
    elif source == "2":
        db_manager.get_all_vacancies("headhunter")
    elif source == "3":
        db_manager.get_avg_salary("headhunter")
    elif source == "4":
        db_manager.get_vacancies_with_higher_salary("headhunter")
    elif source == "5":
        print("Введите поисковое слово:")
        key = input().strip()
        db_manager.get_vacancies_with_keyword("headhunter", key)


if __name__ == "__main__":
    main()
