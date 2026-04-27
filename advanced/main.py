import re
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from config import OLLAMA_ENDPOINT, OLLAMA_MODEL, GENDER, WEIGHT_KG, HEIGHT_CM, AGE, DATE_FORMAT, TIME_FORMAT
from client import OllamaClient, MET
from sheet_writer import SheetWriter

AMBIGUOUS = {"gym", "workout", "exercise", "training", "worked out", "exercised", "trained"}

GYM_EXERCISES = [
    "Weight Training", "Running", "Cycling", "Rowing", "Elliptical",
    "Jump Rope", "HIIT", "CrossFit", "Push-Ups", "Pull-Ups", "Sit-Ups",
    "Boxing", "Yoga", "Pilates", "Stretching", "Zumba", "Martial Arts",
    "Rock Climbing", "Basketball",
]


_DURATION_RE = re.compile(
    r"(\d+)\s*h(?:ours?|r)?(?:\s*(\d+)\s*min(?:utes?)?)?|"
    r"an?\s+hour|"
    r"(\d+)\s*min(?:utes?)?",
    re.IGNORECASE,
)


def _extract_duration(text: str) -> str:
    m = _DURATION_RE.search(text)
    if not m:
        return ""
    if "an hour" in text.lower() or "a hour" in text.lower():
        return "60 mins"
    hours, mins, mins_only = m.group(1), m.group(2), m.group(3)
    if mins_only:
        return f"{mins_only} mins"
    total = int(hours or 0) * 60 + int(mins or 0)
    return f"{total} mins"


def disambiguate(text: str) -> str:
    """If the input is too vague, prompt the user to pick a specific exercise."""
    words = set(text.lower().split())
    if not words & AMBIGUOUS:
        return text
    duration = _extract_duration(text)
    exercises = GYM_EXERCISES
    print("\n  Your input is a bit vague. What did you do specifically?\n")
    for i, name in enumerate(exercises, 1):
        print(f"  {i:>2}) {name}")
    print()
    while True:
        choice = input("  Enter number (or press Enter to describe freely): ").strip()
        if choice == "":
            return text
        if choice.isdigit() and 1 <= int(choice) <= len(exercises):
            chosen = exercises[int(choice) - 1]
            if not duration:
                duration = input(f"  How long did you do {chosen}? (e.g. 45 mins): ").strip()
            return f"{chosen} for {duration}"
        print("  Invalid choice, try again.")


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

    while True:
        exercise_text = input("\nTell me which exercises you did (or 'q' to go back): ").strip()
        if exercise_text.lower() == "q":
            break

        exercise_text = disambiguate(exercise_text)
        exercises = nutritionix.get_exercises(exercise_text)

        today = datetime.now().strftime(DATE_FORMAT)
        now = datetime.now().strftime(TIME_FORMAT)

        print(f"\n  Logged to Google Sheets — {today} at {now}\n")
        for exercise in exercises:
            duration = int(round(exercise["duration_min"]))
            calories = round(exercise["nf_calories"], 2)
            name = exercise["name"].title()

            writer.log_exercise(
                date=today,
                time=now,
                name=name,
                duration_mins=duration,
                calories=calories,
            )
            print(f"  ✓  {name:<20} {duration} min   {calories} kcal")


if __name__ == "__main__":
    main()
