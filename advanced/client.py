import requests


class NutritionixClient:
    """Fetches exercise data from the Nutritionix Natural Language API."""

    def __init__(
        self,
        app_id: str,
        api_key: str,
        endpoint: str,
        gender: str,
        weight_kg: float,
        height_cm: float,
        age: int,
    ) -> None:
        self._app_id = app_id
        self._api_key = api_key
        self._endpoint = endpoint
        self._user_profile = {
            "gender": gender,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "age": age,
        }

    def get_exercises(self, query: str) -> list[dict]:
        """POST a natural-language exercise query. Returns a list of exercise dicts."""
        headers = {
            "x-app-id": self._app_id,
            "x-app-key": self._api_key,
        }
        body = {"query": query, **self._user_profile}
        response = requests.post(self._endpoint, json=body, headers=headers)
        response.raise_for_status()
        return response.json()["exercises"]
