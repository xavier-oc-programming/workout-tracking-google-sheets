# Workout Tracker — Google Sheets

Log workouts to Google Sheets using natural language via Nutritionix and Sheety.

---

## Table of Contents

- [0. Prerequisites](#0-prerequisites)
- [1. Quick start](#1-quick-start)
- [2. Builds comparison](#2-builds-comparison)
- [3. Usage](#3-usage)
- [4. Data flow](#4-data-flow)
- [5. Features](#5-features)
- [6. Navigation flow](#6-navigation-flow)
- [7. Architecture](#7-architecture)
- [8. Module reference](#8-module-reference)
- [9. Configuration reference](#9-configuration-reference)
- [10. Data schema](#10-data-schema)
- [11. Environment variables](#11-environment-variables)
- [12. Design decisions](#12-design-decisions)
- [13. Course context](#13-course-context)
- [14. Dependencies](#14-dependencies)

---

## 0. Prerequisites

### Nutritionix

Sign up for a free developer account at the Nutritionix developer portal.

After logging in, create a new application. You will receive an App ID and API Key.

**Gotcha:** new keys may take a few minutes to activate after creation.

| .env variable | Where to find it |
|---|---|
| `NUTRITIONIX_APP_ID` | Dashboard → your app → App ID |
| `NUTRITIONIX_API_KEY` | Dashboard → your app → API Key |

---

### Sheety

Sheety turns a Google Sheet into a REST API. Sign up at sheety.co using Google.

**Setup:**
1. Create a Google Sheet with these exact column headers in row 1: `date`, `time`, `exercise`, `duration (minutes)`, `calories`
2. Log in to sheety.co → New Project → paste your Google Sheet URL
3. Enable **POST** requests for the sheet tab
4. Enable **Basic Auth** under Project Settings → Authentication → choose a username and password
5. Copy the endpoint URL (e.g. `https://api.sheety.co/[id]/[project]/workouts`)

| .env variable | Where to find it |
|---|---|
| `SHEETY_ENDPOINT` | Project page → your endpoint URL |
| `SHEETY_USERNAME` | The username you set when enabling Basic Auth |
| `SHEETY_PASSWORD` | The password you set when enabling Basic Auth |

---

## 1. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
python menu.py         # select 1 or 2, or run builds directly
```

**Run builds directly:**

```bash
python original/main.py   # course version (uses hardcoded credentials)
python advanced/main.py   # OOP version (reads from .env)
```

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Natural language exercise input | Yes | Yes |
| Nutritionix API integration | Yes | Yes |
| Google Sheets logging via Sheety | Yes | Yes |
| Basic Auth for Sheety | Yes | Yes |
| Credentials from `.env` | No (hardcoded) | Yes |
| OOP modules | No | Yes |
| Config constants centralised | No | Yes |
| Proper error surfacing (`raise_for_status`) | No | Yes |
| Runnable from `menu.py` | — | Yes |

---

## 3. Usage

Both builds prompt for a natural-language exercise description, then log each parsed exercise to Google Sheets.

```
Tell me which exercises you did: I ran 5km and did push-ups for 20 minutes
```

**Example output (advanced):**

```
Logged: Running — 30 min, 301.22 kcal → {'workout': {'id': 2, 'date': '08/04/2026', ...}}
Logged: Push-Ups — 20 min, 115.0 kcal → {'workout': {'id': 3, 'date': '08/04/2026', ...}}
```

**Google Sheet result:**

| date | time | exercise | duration (minutes) | calories |
|---|---|---|---|---|
| 08/04/2026 | 11:32:10 | Running | 30 | 301.22 |
| 08/04/2026 | 11:32:10 | Push-Ups | 20 | 115.0 |

---

## 4. Data flow

```
User input (plain English)
  → POST to Nutritionix /v2/natural/exercise
    body: { query, gender, weight_kg, height_cm, age }
  → Response: list of exercise objects with name, duration_min, nf_calories
    → For each exercise: round duration to int, round calories to 2dp
      → POST to Sheety endpoint with Basic Auth
        body: { workout: { date, time, exercise, duration (minutes), calories } }
          → New row appears in Google Sheet
```

---

## 5. Features

**Both builds**

**Natural language parsing.** Describe your workout in plain English — Nutritionix extracts exercise name, duration, and calories burned automatically.

**Automatic date and time stamping.** Each logged row includes the current date (`dd/mm/yyyy`) and time (`hh:mm:ss`).

**Multi-exercise support.** One input can describe multiple exercises; each is logged as a separate row.

**Secure Sheety access.** HTTP Basic Authentication protects the Sheety endpoint from unauthorised writes.

**Advanced build only**

**OOP module split.** `NutritionixClient` handles all API fetching; `SheetWriter` handles all Sheety posting. Each is independently testable.

**Centralised config.** All URLs, formats, and user profile defaults live in `config.py` — no magic values elsewhere.

**Proper error surfacing.** `response.raise_for_status()` raises an `HTTPError` on 4xx/5xx responses rather than silently returning empty data.

**Credentials from `.env`.** No hardcoded secrets. All credentials are loaded via `python-dotenv`.

---

## 6. Navigation flow

### Terminal menu tree

```
python menu.py
├── 1 → original/main.py  (course script)
├── 2 → advanced/main.py  (OOP refactor)
└── q → exit
```

### Execution flow (advanced build)

```
advanced/main.py starts
  │
  ├── Load .env credentials
  ├── Instantiate NutritionixClient + SheetWriter
  ├── Prompt user: "Tell me which exercises you did:"
  │
  ├── POST query to Nutritionix API
  │     ├── HTTP error → raise_for_status() → exception propagates to caller
  │     └── Success → list of exercise dicts returned
  │
  └── For each exercise:
        ├── Round duration (int) and calories (2dp)
        ├── POST row to Sheety
        │     ├── HTTP error → raise_for_status() → exception propagates
        │     └── Success → print confirmation + created row
        └── Continue to next exercise
```

---

## 7. Architecture

```
workout-tracking-google-sheets/
│
├── menu.py                   # Interactive menu — launches builds via subprocess
├── art.py                    # LOGO ASCII art printed by menu.py
├── requirements.txt          # pip dependencies + Python version note
├── .env.example              # Credential placeholders (committed)
├── .env                      # Real credentials (gitignored)
├── README.md                 # This file
│
├── original/
│   └── main.py               # Verbatim course script (hardcoded credentials)
│
├── advanced/
│   ├── config.py             # All constants: endpoint, user profile, date format
│   ├── client.py             # NutritionixClient — fetches exercise data from API
│   ├── sheet_writer.py       # SheetWriter — posts exercise rows to Sheety
│   └── main.py               # Orchestrator — wires client + writer together
│
└── docs/
    └── COURSE_NOTES.md       # Original course exercise description
```

---

## 8. Module reference

### `advanced/client.py` — `NutritionixClient`

| Method | Returns | Description |
|---|---|---|
| `__init__(app_id, api_key, endpoint, gender, weight_kg, height_cm, age)` | `None` | Stores credentials and user profile |
| `get_exercises(query: str)` | `list[dict]` | POSTs query to Nutritionix; returns list of exercise dicts |

### `advanced/sheet_writer.py` — `SheetWriter`

| Method | Returns | Description |
|---|---|---|
| `__init__(endpoint, username, password)` | `None` | Stores Sheety endpoint and Basic Auth credentials |
| `log_exercise(date, time, name, duration_mins, calories)` | `dict` | POSTs one exercise row to Sheety; returns the created row |

---

## 9. Configuration reference

All constants are in [advanced/config.py](advanced/config.py).

| Constant | Default | Description |
|---|---|---|
| `NUTRITIONIX_ENDPOINT` | `https://trackapi.nutritionix.com/v2/natural/exercise` | Nutritionix Natural Language API URL |
| `GENDER` | `"male"` | User gender sent to Nutritionix for calorie calculation |
| `WEIGHT_KG` | `70` | User weight in kg |
| `HEIGHT_CM` | `175` | User height in cm |
| `AGE` | `27` | User age in years |
| `DATE_FORMAT` | `"%d/%m/%Y"` | Date format for the Google Sheet |
| `TIME_FORMAT` | `"%X"` | Time format for the Google Sheet (`hh:mm:ss`) |

---

## 10. Data schema

### Nutritionix API request body

```json
{
  "query": "I ran 5km and did push-ups for 20 minutes",
  "gender": "male",
  "weight_kg": 70,
  "height_cm": 175,
  "age": 27
}
```

### Nutritionix API response (one exercise object)

```json
{
  "name": "running",
  "duration_min": 30.0,
  "nf_calories": 301.22
}
```

### Sheety POST request body

```json
{
  "workout": {
    "date": "08/04/2026",
    "time": "11:32:10",
    "exercise": "Running",
    "duration (minutes)": 30,
    "calories": 301.22
  }
}
```

### Sheety POST response

```json
{
  "workout": {
    "id": 2,
    "date": "08/04/2026",
    "time": "11:32:10",
    "exercise": "Running",
    "duration (minutes)": 30,
    "calories": 301.22
  }
}
```

### Google Sheet row format

| date | time | exercise | duration (minutes) | calories |
|---|---|---|---|---|
| 08/04/2026 | 11:32:10 | Running | 30 | 301.22 |

---

## 11. Environment variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Required | Description |
|---|---|---|
| `NUTRITIONIX_APP_ID` | Yes | Nutritionix App ID |
| `NUTRITIONIX_API_KEY` | Yes | Nutritionix API Key |
| `SHEETY_ENDPOINT` | Yes | Full Sheety endpoint URL for your sheet tab |
| `SHEETY_USERNAME` | Yes | Basic Auth username set in Sheety |
| `SHEETY_PASSWORD` | Yes | Basic Auth password set in Sheety |

---

## 12. Design decisions

**`config.py` — zero magic numbers.** Every URL, format string, and user profile value lives in one place. Change your weight once; it applies everywhere.

**Separate `NutritionixClient` and `SheetWriter` modules.** Each class has one responsibility and can be tested in isolation. Swapping the HTTP client or the sheet backend requires touching one file, not the orchestrator.

**Credentials via `.env`, never hardcoded.** Hardcoded secrets end up in git history and leak when repos are made public. `.env` stays local; `.env.example` documents what is needed without exposing values.

**`.env.example` committed, `.env` gitignored.** Anyone cloning the repo knows exactly which variables to provide without seeing real values.

**`Path(__file__).parent` for all file paths.** The script runs correctly whether launched from `menu.py` (which sets `cwd` to the script's directory) or directly from the terminal.

**Pure-logic modules raise exceptions instead of `sys.exit()`.** `NutritionixClient.get_exercises` and `SheetWriter.log_exercise` raise `requests.HTTPError` on failure. `main.py` decides how to handle it — a design that keeps the modules reusable.

**`sys.path.insert` pattern.** Ensures sibling imports (`from config import ...`) resolve correctly when the script is launched via `subprocess.run` from `menu.py`.

**`subprocess.run` + `cwd=` in `menu.py`.** Each build runs in its own working directory, so relative paths inside each script resolve as if run directly.

**`while True` in `menu.py` vs recursion.** Re-calling `main()` after each build would grow the call stack unboundedly. A simple loop is safe and clear.

**Console cleared before every menu render, not after errors.** Clearing after an invalid choice would erase the error message before the user reads it. The `clear` flag preserves errors while keeping the menu clean on normal navigation.

---

## 13. Course context

Built as Day 38 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:** HTTP POST requests, custom headers, JSON bodies, parsing API responses, `datetime` for timestamps, `requests.auth.HTTPBasicAuth`, chaining two APIs together.

**The advanced build extends into:** OOP module design (single-responsibility classes), centralised config, environment variable management with `python-dotenv`, proper HTTP error handling with `raise_for_status()`.

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for full concept breakdown.

---

## 14. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `requests` | `original/main.py`, `advanced/client.py`, `advanced/sheet_writer.py` | HTTP POST to Nutritionix and Sheety |
| `requests.auth.HTTPBasicAuth` | `original/main.py`, `advanced/sheet_writer.py` | Basic Authentication for Sheety |
| `python-dotenv` | `advanced/main.py` | Load credentials from `.env` |
| `datetime` | `original/main.py`, `advanced/main.py` | Generate date and time stamps |
| `os` | `menu.py`, `advanced/main.py` | Clear console; read env vars |
| `sys` | `menu.py`, `advanced/main.py` | Python executable path; `sys.path.insert` |
| `subprocess` | `menu.py` | Launch builds as child processes |
| `pathlib.Path` | `menu.py`, `advanced/main.py` | Resolve file paths portably |
