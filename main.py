import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from math import ceil

"""
Workout Tracking Using Google Sheets
Steps 1–5 implemented in one script:
  1) Setup API credentials + Google Sheet
  2) Get exercise stats from Nutritionix (natural language)
  3) Connect Google Sheet to Sheety (project + endpoint)
  4) Save parsed exercises into the sheet (POST to Sheety)
  5) Secure Sheety with Basic Authentication
"""

# ------------------- Step 1: User stats and credentials ------------------- #
GENDER = "male"
WEIGHT_KG = 70
HEIGHT_CM = 175
AGE = 27

APP_ID = "8cd14c3a"
API_KEY = "125aa2481fda7aa382b5eda9052d986f"

exercise_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"
sheet_endpoint = "https://api.sheety.co/cce7939510706ad6a4ec617e2e435c61/workoutTracking/workouts"

# ------------------- Step 5: Sheety Basic Auth credentials ------------------- #
SHEETY_USERNAME = "workout_user01"
SHEETY_PASSWORD = "myexercise01"

# ------------------- Step 2: Get user input and query Nutritionix ----------- #
exercise_text = input("Tell me which exercises you did: ")

headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,
}

parameters = {
    "query": exercise_text,
    "gender": GENDER,
    "weight_kg": WEIGHT_KG,
    "height_cm": HEIGHT_CM,
    "age": AGE
}

response = requests.post(exercise_endpoint, json=parameters, headers=headers)
result = response.json()

# ------------------- Step 4: Format and send to Sheety ------------------- #
today_date = datetime.now().strftime("%d/%m/%Y")
now_time = datetime.now().strftime("%X")

for exercise in result["exercises"]:
    mins = int(round(exercise["duration_min"]))  # Store as integer (not "50 min")
    calories = round(exercise["nf_calories"], 2)

    sheet_inputs = {
        "workout": {
            "date": today_date,
            "time": now_time,
            "exercise": exercise["name"].title(),
            "duration (minutes)": mins,  
            "calories": calories
        }
    }


    sheet_response = requests.post(
        sheet_endpoint,
        json=sheet_inputs,
        auth=HTTPBasicAuth(SHEETY_USERNAME, SHEETY_PASSWORD)
    )

    print(sheet_response.text)
