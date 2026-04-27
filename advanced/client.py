import json
import requests

SYNONYMS: dict[str, str] = {
    "jogging": "Running",
    "jog": "Running",
    "sprinting": "Running",
    "sprint": "Running",
    "swimming": "Swimming",
    "swam": "Swimming",
    "swim": "Swimming",
    "cycling": "Cycling",
    "biking": "Cycling",
    "bike": "Cycling",
    "walking": "Walking",
    "walk": "Walking",
    "hiking": "Hiking",
    "hike": "Hiking",
    "push-ups": "Push-Ups",
    "pushups": "Push-Ups",
    "push ups": "Push-Ups",
    "pull-ups": "Pull-Ups",
    "pullups": "Pull-Ups",
    "pull ups": "Pull-Ups",
    "sit-ups": "Sit-Ups",
    "situps": "Sit-Ups",
    "sit ups": "Sit-Ups",
}

# MET values per exercise (Metabolic Equivalent of Task)
# Source: Compendium of Physical Activities
MET: dict[str, float] = {
    "Running":          9.8,
    "Jogging":          7.0,
    "Walking":          3.5,
    "Swimming":         6.0,
    "Cycling":          7.5,
    "Hiking":           6.0,
    "Yoga":             3.0,
    "Pilates":          3.0,
    "Push-Ups":         3.8,
    "Pull-Ups":         4.0,
    "Sit-Ups":          3.0,
    "Weight Training":  3.5,
    "Jump Rope":        12.0,
    "Elliptical":       5.0,
    "Rowing":           7.0,
    "Dancing":          5.0,
    "Boxing":           7.8,
    "Martial Arts":     7.0,
    "Stretching":       2.5,
    "Basketball":       6.5,
    "Football":         8.0,
    "Tennis":           7.3,
    "Rock Climbing":    8.0,
    "Skiing":           7.0,
    "CrossFit":         8.0,
    "HIIT":             8.0,
    "Zumba":            6.0,
}
DEFAULT_MET = 5.0


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

    def _calories(self, name: str, duration_min: float) -> float:
        met = MET.get(name, DEFAULT_MET)
        return round(met * self._weight_kg * (duration_min / 60), 2)

    def get_exercises(self, query: str) -> list[dict]:
        """Send a natural-language exercise query to Ollama. Returns a list of exercise dicts."""
        prompt = (
            f"Extract the unique exercises from this input and return ONLY a valid JSON array. "
            f"List each distinct exercise exactly once — do not repeat or split the same activity. "
            f"Each object must have exactly these keys: "
            f"\"name\" (string), \"duration_min\" (number). "
            f"The name must be the standard well-known exercise name (e.g. 'Swimming', 'Running', 'Cycling', 'Push-Ups', 'Yoga') — never past tense, never a conjugated verb. "
            f"All values must be non-null. "
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

        valid = [
            e for e in exercises
            if isinstance(e, dict)
            and e.get("duration_min") is not None
            and e.get("name")
        ]
        for e in valid:
            e["name"] = SYNONYMS.get(e["name"].lower(), e["name"])
            e["nf_calories"] = self._calories(e["name"], e["duration_min"])
        return valid
