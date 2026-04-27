# Workout Tracker — Google Sheets

Log workouts to Google Sheets using natural language and a local AI model.

Type a plain-English description of your workout — "I ran 5km and did 20 minutes of yoga" — and the script parses it, estimates duration and calories burned, then writes each exercise as a timestamped row directly into a Google Sheet. No manual data entry, no spreadsheet formulas to maintain.

The project is built in two versions. The **original** build is the course script from Day 38 of 100 Days of Code: a single file, hardcoded credentials, procedural top-to-bottom execution. It is kept as a historical reference of the course exercise — it used Nutritionix for natural language parsing, but **Nutritionix discontinued its free tier** during development so the original build no longer functions. The **advanced** build refactors it into separate classes (`OllamaClient`, `SheetWriter`), centralises all constants in `config.py`, loads credentials from a `.env` file, and replaces Nutritionix with a locally-running Ollama LLM — meaning no API keys, no accounts, and no cost for anyone who clones the repo.

Both versions log to Google Sheets via [Sheety](https://sheety.co), which wraps any Google Sheet in a REST API so you can POST rows with a plain HTTP request.

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
- [13. Challenges](#13-challenges)
- [14. Course context](#14-course-context)
- [15. Dependencies](#15-dependencies)

---

## 0. Prerequisites

### Ollama (advanced build only)

The advanced build uses a locally-running LLM via [Ollama](https://ollama.com) instead of a cloud API. No account or API key required — everything runs on your machine.

**Install Ollama:**

```bash
brew install ollama        # macOS
# or download from https://ollama.com
```

**Start Ollama and pull the model:**

```bash
brew services start ollama   # start as a background service
ollama pull llama3.2         # ~2GB download, one-time only
```

Once Ollama is running and the model is pulled, no further setup is needed — the advanced build connects to it automatically at `http://localhost:11434`.

---

### Sheety (both builds)

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

### Nutritionix (original build only)

The original build uses Nutritionix for natural language parsing. Note: **the Nutritionix free tier has been discontinued** — the original build is kept as a historical reference of the course exercise, but may no longer work with a free account.

---

## 1. Quick start

**Advanced build (recommended):**

```bash
# 1. Start Ollama and ensure the model is ready
brew services start ollama
ollama pull llama3.2         # skip if already pulled

# 2. Clone and install
pip install -r requirements.txt
cp .env.example .env         # fill in your Sheety credentials only

# 3. Run
python menu.py               # select 2, or run directly:
python advanced/main.py
```

**Original build (course reference):**

```bash
pip install -r requirements.txt
python original/main.py      # uses hardcoded credentials — may fail if Nutritionix free tier is inactive
```

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---|---|---|
| Natural language exercise input | Yes | Yes |
| Exercise parsing | Nutritionix API (cloud) | Ollama LLM (local) |
| Google Sheets logging via Sheety | Yes | Yes |
| Basic Auth for Sheety | Yes | Yes |
| Requires API key / account | Yes (Nutritionix) | No |
| Works offline | No | Yes (after model pull) |
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
Logged: Running — 30 min, 290.0 kcal → {'workout': {'id': 2, 'date': '27/04/2026', ...}}
Logged: Push-Ups — 20 min, 112.0 kcal → {'workout': {'id': 3, 'date': '27/04/2026', ...}}
```

**Google Sheet result:**

| date | time | exercise | duration (minutes) | calories |
|---|---|---|---|---|
| 27/04/2026 | 11:32:10 | Running | 30 | 290.0 |
| 27/04/2026 | 11:32:10 | Push-Ups | 20 | 112.0 |

---

## 4. Data flow

**Advanced build:**

```
User input (plain English)
  → POST to Ollama local API (localhost:11434/api/chat)
      body: { model, messages: [{ role: "user", content: prompt with user stats }] }
  → Response: JSON array of exercise objects with name, duration_min, nf_calories
    → For each exercise: round duration to int, round calories to 2dp
      → POST to Sheety endpoint with Basic Auth
          body: { workout: { date, time, exercise, duration (minutes), calories } }
            → New row appears in Google Sheet
```

**Original build:**

```
User input (plain English)
  → POST to Nutritionix /v2/natural/exercise  [may be inactive on free tier]
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

**Natural language parsing.** Describe your workout in plain English — the parser extracts exercise name, duration, and estimated calories burned automatically.

**Automatic date and time stamping.** Each logged row includes the current date (`dd/mm/yyyy`) and time (`hh:mm:ss`).

**Multi-exercise support.** One input can describe multiple exercises; each is logged as a separate row.

**Secure Sheety access.** HTTP Basic Authentication protects the Sheety endpoint from unauthorised writes.

**Advanced build only**

**Local LLM parsing via Ollama.** Exercise descriptions are interpreted by `llama3.2` running entirely on your machine — no cloud account, no API key, no usage limits, no cost.

**OOP module split.** `OllamaClient` handles all LLM interaction; `SheetWriter` handles all Sheety posting. Each is independently testable.

**Centralised config.** All URLs, model names, formats, and user profile defaults live in `config.py` — no magic values elsewhere.

**Proper error surfacing.** `response.raise_for_status()` raises an `HTTPError` on 4xx/5xx responses rather than silently returning empty data.

**Credentials from `.env`.** No hardcoded secrets. All Sheety credentials are loaded via `python-dotenv`.

---

## 6. Navigation flow

### Terminal menu tree

```
python menu.py
├── 1 → original/main.py  (course script — Nutritionix + Sheety)
├── 2 → advanced/main.py  (OOP refactor — Ollama + Sheety)
└── q → exit
```

### Execution flow (advanced build)

```
advanced/main.py starts
  │
  ├── Load .env credentials (Sheety only)
  ├── Instantiate OllamaClient + SheetWriter
  ├── Prompt user: "Tell me which exercises you did:"
  │
  ├── POST prompt to Ollama local API
  │     ├── HTTP error → raise_for_status() → exception propagates to caller
  │     └── Success → parse JSON → list of exercise dicts returned
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
│   └── main.py               # Course script — Nutritionix + Sheety, hardcoded credentials
│
├── advanced/
│   ├── config.py             # All constants: Ollama endpoint/model, user profile, date format
│   ├── client.py             # OllamaClient — sends exercise queries to local Ollama LLM
│   ├── sheet_writer.py       # SheetWriter — posts exercise rows to Sheety
│   └── main.py               # Orchestrator — wires client + writer together
│
└── docs/
    └── COURSE_NOTES.md       # Original course exercise description
```

---

## 8. Module reference

### `advanced/client.py` — `OllamaClient`

| Method | Returns | Description |
|---|---|---|
| `__init__(endpoint, model, weight_kg, height_cm, age, gender)` | `None` | Stores Ollama config and user profile for calorie estimation |
| `get_exercises(query: str)` | `list[dict]` | POSTs prompt to local Ollama API; parses and returns list of exercise dicts |

Each dict in the returned list contains: `name` (str), `duration_min` (float), `nf_calories` (float).

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
| `OLLAMA_ENDPOINT` | `http://localhost:11434/api/chat` | Local Ollama chat API URL |
| `OLLAMA_MODEL` | `"llama3.2"` | Model name to use for exercise parsing |
| `GENDER` | `"male"` | User gender — passed to the LLM for calorie estimation |
| `WEIGHT_KG` | `70` | User weight in kg |
| `HEIGHT_CM` | `175` | User height in cm |
| `AGE` | `27` | User age in years |
| `DATE_FORMAT` | `"%d/%m/%Y"` | Date format for the Google Sheet |
| `TIME_FORMAT` | `"%X"` | Time format for the Google Sheet (`hh:mm:ss`) |

---

## 10. Data schema

### Ollama API request body (advanced build)

```json
{
  "model": "llama3.2",
  "messages": [
    {
      "role": "user",
      "content": "Extract the unique exercises from this input and return ONLY a valid JSON array. List each distinct exercise exactly once — do not repeat or split the same activity. Each object must have exactly these keys: \"name\" (string), \"duration_min\" (number), \"nf_calories\" (number). The name must be the standard well-known exercise name (e.g. 'Swimming', 'Running', 'Cycling', 'Push-Ups', 'Yoga') — never past tense, never a conjugated verb. All values must be non-null numbers. Estimate calories burned using: weight 70kg, height 175cm, age 27, gender male. Input: \"I ran 5km and did push-ups for 20 minutes\""
    }
  ],
  "stream": false,
  "format": "json"
}
```

### Ollama API response → parsed exercise array

```json
[
  { "name": "Running", "duration_min": 30, "nf_calories": 290.0 },
  { "name": "Push-Ups", "duration_min": 20, "nf_calories": 112.0 }
]
```

### Sheety POST request body

```json
{
  "workout": {
    "date": "27/04/2026",
    "time": "11:32:10",
    "exercise": "Running",
    "duration (minutes)": 30,
    "calories": 290.0
  }
}
```

### Sheety POST response

```json
{
  "workout": {
    "id": 2,
    "date": "27/04/2026",
    "time": "11:32:10",
    "exercise": "Running",
    "duration (minutes)": 30,
    "calories": 290.0
  }
}
```

### Google Sheet row format

| date | time | exercise | duration (minutes) | calories |
|---|---|---|---|---|
| 27/04/2026 | 11:32:10 | Running | 30 | 290.0 |

---

## 11. Environment variables

Copy `.env.example` to `.env` and fill in your Sheety values. The advanced build no longer requires Nutritionix credentials.

| Variable | Required by | Description |
|---|---|---|
| `SHEETY_ENDPOINT` | Both builds | Full Sheety endpoint URL for your sheet tab |
| `SHEETY_USERNAME` | Both builds | Basic Auth username set in Sheety |
| `SHEETY_PASSWORD` | Both builds | Basic Auth password set in Sheety |

> The original build reads Nutritionix credentials and Sheety credentials directly from hardcoded variables in `original/main.py`, not from `.env`.

---

## 12. Design decisions

**`OllamaClient` instead of a cloud NLP API.** The advanced build deliberately routes exercise parsing through a local LLM rather than any cloud service. This means anyone who clones the repo can run it immediately after pulling a model — no account, no key, no rate limit, no cost ever. The tradeoff is a ~2GB one-time model download and the requirement that Ollama is running locally.

**`format: "json"` in the Ollama request.** Ollama's `format` parameter constrains the model to output valid JSON, avoiding the need to strip markdown fences or prose from the response.

**Flexible response parsing in `OllamaClient.get_exercises`.** The LLM may return a bare array, a single exercise dict, or an array wrapped in a key (`exercises`, `workouts`, `results`). The client handles all forms rather than assuming a fixed shape, and filters out any entry with a `null` name, duration, or calorie value before returning.

**Normalised exercise names in the prompt.** Early testing showed the model returning past-tense verbs as names ("Swam", "Ran") rather than standard exercise names, causing inconsistent data in the sheet. The prompt explicitly instructs the model to use the well-known exercise name (e.g. "Swimming", "Running", "Push-Ups") and never a conjugated or past-tense verb. The prompt also asks for each distinct exercise exactly once to prevent the model from returning duplicate entries for the same activity.

**User profile passed in the prompt, not as API parameters.** Unlike Nutritionix (which accepted `gender`, `weight_kg`, etc. as structured fields), the LLM receives user stats as natural language in the prompt. This is intentionally simple — the model uses them to improve calorie estimates without requiring a custom schema.

**`config.py` — zero magic numbers.** Every URL, model name, format string, and user profile value lives in one place. Change your weight once; it applies everywhere.

**Separate `OllamaClient` and `SheetWriter` modules.** Each class has one responsibility and can be tested in isolation. Swapping the LLM backend or the sheet backend requires touching one file, not the orchestrator.

**Credentials via `.env`, never hardcoded.** Hardcoded secrets end up in git history and leak when repos are made public. `.env` stays local; `.env.example` documents what is needed without exposing values.

**`.env.example` committed, `.env` gitignored.** Anyone cloning the repo knows exactly which variables to provide without seeing real values.

**`Path(__file__).parent` for all file paths.** The script runs correctly whether launched from `menu.py` (which sets `cwd` to the script's directory) or directly from the terminal.

**Pure-logic modules raise exceptions instead of `sys.exit()`.** `OllamaClient.get_exercises` and `SheetWriter.log_exercise` raise `requests.HTTPError` on failure. `main.py` decides how to handle it — a design that keeps the modules reusable.

**`sys.path.insert` pattern.** Ensures sibling imports (`from config import ...`) resolve correctly when the script is launched via `subprocess.run` from `menu.py`.

**`subprocess.run` + `cwd=` in `menu.py`.** Each build runs in its own working directory, so relative paths inside each script resolve as if run directly.

**`while True` in `menu.py` vs recursion.** Re-calling `main()` after each build would grow the call stack unboundedly. A simple loop is safe and clear.

**Console cleared before every menu render, not after errors.** Clearing after an invalid choice would erase the error message before the user reads it. The `clear` flag preserves errors while keeping the menu clean on normal navigation.

---

## 13. Challenges

### Nutritionix discontinued its free tier

The course exercise was designed around the Nutritionix Natural Language API, which accepted workout descriptions in plain English and returned structured exercise data (name, duration, calories) calibrated to the user's body stats. This was the only free cloud API that handled the full natural language → structured exercise pipeline in a single call.

During development, Nutritionix announced that the public free-access tier had been permanently discontinued. Existing free accounts hit their limit, and new free signups were no longer offered. This broke the core feature of the project.

**Investigation:** We surveyed all known free alternatives:

| API | Free? | Natural language? | Calories? |
|---|---|---|---|
| API Ninjas Calories Burned | Yes | No — structured input only | Yes |
| wger | Yes, open-source | No | Manual (MET formula) |
| ExerciseDB | Yes | No | No |
| Nutritionix | No longer | Yes | Yes |

No free cloud API offered the full natural language → calories pipeline that Nutritionix provided.

**Constraint:** The solution had to remain free for any user who clones the repo, with no mandatory sign-ups or API keys. This ruled out paid tiers and APIs that require registration, since the whole point of the project is that anyone should be able to run it.

**Solution:** Replace Nutritionix with a locally-running LLM via [Ollama](https://ollama.com). The `OllamaClient` sends the user's exercise description to `llama3.2` running at `localhost:11434`, prompts it to return a structured JSON array, and parses the result. The user profile (weight, height, age, gender) is included in the prompt so the model can estimate calories in the same way Nutritionix did.

This approach:
- Requires no API key or account
- Is free forever, for any user
- Preserves the natural language input experience
- Is still a genuine REST API call (POST to `localhost:11434/api/chat`) — the learning objective of the exercise is fully intact
- Works offline after the one-time model pull

The only new setup step for users is installing Ollama and pulling the model (~2GB, one-time).

### LLM response inconsistency — exercise names and duplicates

After switching to Ollama, two prompt engineering issues emerged during testing:

**Past-tense names.** When the user typed "I swam for an hour", the model returned `"name": "Swam"` — a past-tense verb — instead of the standard exercise name "Swimming". This caused inconsistent data in the Google Sheet (one row logged as "Swam", the next as "Swimming" for the same activity).

**Duplicate entries.** For a single-exercise input, the model occasionally returned two entries for the same activity (e.g. both "Swimming" and "Swim"), with one of them missing a `duration_min` value, crashing the loop with a `TypeError`.

**Solution:** Two-part fix:
1. The prompt was updated to explicitly require standard well-known exercise names ("Swimming", "Running", "Push-Ups") and forbid past-tense or conjugated verbs. Examples were included directly in the prompt to anchor the model's output.
2. The prompt instructs the model to list each distinct exercise exactly once. A filter was added in `get_exercises` to strip any returned entry missing a `name`, `duration_min`, or `nf_calories` value, so a malformed model response can never crash the logging loop.

---

## 14. Course context

Built as Day 38 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:** HTTP POST requests, custom headers, JSON bodies, parsing API responses, `datetime` for timestamps, `requests.auth.HTTPBasicAuth`, chaining two APIs together.

**The advanced build extends into:** OOP module design (single-responsibility classes), centralised config, environment variable management with `python-dotenv`, proper HTTP error handling with `raise_for_status()`, local LLM integration via Ollama, structured JSON prompt engineering.

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for full concept breakdown.

---

## 15. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `requests` | `original/main.py`, `advanced/client.py`, `advanced/sheet_writer.py` | HTTP POST to Ollama and Sheety |
| `requests.auth.HTTPBasicAuth` | `original/main.py`, `advanced/sheet_writer.py` | Basic Authentication for Sheety |
| `python-dotenv` | `advanced/main.py` | Load Sheety credentials from `.env` |
| `json` | `advanced/client.py` | Parse JSON response from Ollama |
| `datetime` | `original/main.py`, `advanced/main.py` | Generate date and time stamps |
| `os` | `menu.py`, `advanced/main.py` | Clear console; read env vars |
| `sys` | `menu.py`, `advanced/main.py` | Python executable path; `sys.path.insert` |
| `subprocess` | `menu.py` | Launch builds as child processes |
| `pathlib.Path` | `menu.py`, `advanced/main.py` | Resolve file paths portably |

**External tool (not a pip package):**

| Tool | Install | Purpose |
|---|---|---|
| [Ollama](https://ollama.com) | `brew install ollama` | Runs `llama3.2` locally; exposes REST API at `localhost:11434` |
