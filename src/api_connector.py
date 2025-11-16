from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


class VacancyAPI(ABC):
    """
    Абстрактный класс для работы с API сервисов с вакансиями.
    Определяет интерфейс для получения вакансий с различных платформ.
    """

    def __init__(self):
        """Инициализация базового класса."""
        self._base_url: str = ""
        self._headers: Dict[str, str] = {}
        self._params: Dict[str, Any] = {}

    @abstractmethod
    def _connect_to_api(self) -> bool:
        pass

    @abstractmethod
    def get_vacancies(self, employer_ids: List[str]) -> List[Dict[str, Any]]:
        pass


class HeadHunterAPI(VacancyAPI):
    """
    Класс для работы с API HeadHunter.
    Наследуется от абстрактного класса VacancyAPI.
    """

    def __init__(self):
        super().__init__()
        self._base_url = (
            "https://api.hh.ru/vacancies"  # Верный URL для получения вакансий
        )
        self._headers = {"User-Agent": "HH-User-Agent"}
        self._params = {"page": 0, "per_page": 100}

    def _connect_to_api(self) -> bool:
        try:
            response = requests.get(self._base_url, headers=self._headers, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Произошла ошибка при проверке связи с API: {e}")
            return False

    def get_vacancies(self, employer_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Получает список вакансий по указанным идентификаторам работодателей.

        Args:
            employer_ids (List[str]): Список идентификаторов работодателей для поиска вакансий

        Returns:
            List[Dict[str, Any]]: Список вакансий в формате словарей
        """
        if not self._connect_to_api():
            raise ConnectionError("Ошибка соединения с API HeadHunter.")

        all_vacancies = []

        for employer_id in employer_ids:
            self._params["employer_id"] = employer_id
            self._params["page"] = 0
            current_page = 0
            total_pages = 0

            while current_page <= min(total_pages, 20):
                try:
                    response = requests.get(
                        self._base_url,
                        headers=self._headers,
                        params=self._params,
                        timeout=10,
                    )

                    if response.status_code != 200:
                        break

                    data = response.json()
                    page_vacancies = data.get("items", [])

                    if len(page_vacancies) > 0:
                        all_vacancies.extend(page_vacancies)
                        total_pages = data.get("pages", 0)
                        current_page += 1
                        self._params["page"] = current_page
                    else:
                        break

                except requests.RequestException as e:
                    print(f"Произошла ошибка при получении данных: {e}")
                    break

        return all_vacancies
