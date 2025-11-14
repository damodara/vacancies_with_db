from src.api_connector import HeadHunterAPI
from src.utils import DBManager

def main():
    employer_ids = [
        "1907894",  # 1 red
        # "1455",  # 2 hh.ru
        # "4352",  # 3 pochta
        # "1942330",  # 4 pyatyorochka
        # "1122462",  # 5 skyENG
        # "895945",  # 6 Правительство Москвы
        # "2748",  # 7 Ростелеком
        # "4181",  # 8 Банк ВТБ
        "4029257",  # 9 РУСАЛ
        # "9694561",  # 10 Яндекс.Еда
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
    db_manager.get_companies_and_vacancies_count(loaded_vacancies)
    db_manager.get_all_vacancies(loaded_vacancies)


if __name__ == '__main__':
    main()