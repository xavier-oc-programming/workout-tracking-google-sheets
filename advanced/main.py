import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from config import OLLAMA_ENDPOINT, OLLAMA_MODEL, GENDER, WEIGHT_KG, HEIGHT_CM, AGE, DATE_FORMAT, TIME_FORMAT
from client import OllamaClient
from sheet_writer import SheetWriter


def main() -> None:
    nutritionix = OllamaClient(
        endpoint=OLLAMA_ENDPOINT,
        model=OLLAMA_MODEL,
        gender=GENDER,
        weight_kg=WEIGHT_KG,
        height_cm=HEIGHT_CM,
        age=AGE,
    )
    writer = SheetWriter(
        endpoint=os.getenv("SHEETY_ENDPOINT", ""),
        username=os.getenv("SHEETY_USERNAME", ""),
        password=os.getenv("SHEETY_PASSWORD", ""),
    )

    exercise_text = input("Tell me which exercises you did: ")
    exercises = nutritionix.get_exercises(exercise_text)

    today = datetime.now().strftime(DATE_FORMAT)
    now = datetime.now().strftime(TIME_FORMAT)

    for exercise in exercises:
        duration = int(round(exercise["duration_min"]))
        calories = round(exercise["nf_calories"], 2)
        name = exercise["name"].title()

        row = writer.log_exercise(
            date=today,
            time=now,
            name=name,
            duration_mins=duration,
            calories=calories,
        )
        print(f"Logged: {name} — {duration} min, {calories} kcal → {row}")


if __name__ == "__main__":
    main()
