import json
import requests


class OllamaClient:
    """Parses natural-language exercise input using a local Ollama LLM."""

    def __init__(
        self,
        endpoint: str,
        model: str,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
    ) -> None:
        self._endpoint = endpoint
        self._model = model
        self._weight_kg = weight_kg
        self._height_cm = height_cm
        self._age = age
        self._gender = gender

    def get_exercises(self, query: str) -> list[dict]:
        """Send a natural-language exercise query to Ollama. Returns a list of exercise dicts."""
        prompt = (
            f"Extract the unique exercises from this input and return ONLY a valid JSON array. "
            f"List each distinct exercise exactly once — do not repeat or split the same activity. "
            f"Each object must have exactly these keys: "
            f"\"name\" (string), \"duration_min\" (number), \"nf_calories\" (number). "
            f"All values must be non-null numbers. "
            f"Estimate calories burned using: weight {self._weight_kg}kg, "
            f"height {self._height_cm}cm, age {self._age}, gender {self._gender}. "
            f"Input: \"{query}\""
        )
        body = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": "json",
        }
        response = requests.post(self._endpoint, json=body)
        response.raise_for_status()
        content = response.json()["message"]["content"]
        data = json.loads(content)
        if isinstance(data, list):
            exercises = data
        elif isinstance(data, dict) and "name" in data:
            exercises = [data]
        else:
            for key in ("exercises", "workouts", "results"):
                if key in data:
                    exercises = data[key]
                    break
            else:
                exercises = list(data.values())[0]
        return [
            e for e in exercises
            if isinstance(e, dict)
            and e.get("duration_min") is not None
            and e.get("nf_calories") is not None
            and e.get("name")
        ]
