import requests
from requests.auth import HTTPBasicAuth


class SheetWriter:
    """Logs exercise rows to a Google Sheet via the Sheety API."""

    def __init__(self, endpoint: str, username: str, password: str) -> None:
        self._endpoint = endpoint
        self._auth = HTTPBasicAuth(username, password)

    def log_exercise(
        self,
        date: str,
        time: str,
        name: str,
        duration_mins: int,
        calories: float,
    ) -> dict:
        """POST one exercise row to the Sheety endpoint. Returns the created row dict."""
        payload = {
            "workout": {
                "date": date,
                "time": time,
                "exercise": name,
                "duration (minutes)": duration_mins,
                "calories": calories,
            }
        }
        response = requests.post(self._endpoint, json=payload, auth=self._auth)
        response.raise_for_status()
        return response.json()
