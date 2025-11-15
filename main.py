from src.api_connector import HeadHunterAPI
from src.utils import DBManager
from config import config

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

    # # Печать первых трех полученных вакансий
    # for i, vacancy in enumerate(loaded_vacancies[:3]):
    #     print(f"Вакансия №{i + 1}:")
    #     print(f"- Название: {vacancy['name']}")
    #     print(f"- Компания: {vacancy['employer']['name']}\n")
    db_manager = DBManager()
    params = config()
    db_manager.create_db("headhunter", params)
    db_manager.get_companies_and_vacancies_count(loaded_vacancies, "headhunter")
    # db_manager.get_all_vacancies(loaded_vacancies)
    # db_manager.get_avg_salary(loaded_vacancies)




if __name__ == '__main__':
    main()