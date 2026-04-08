# Course Notes — Day 38: Workout Tracking Using Google Sheets

## Exercise description

Build a workout tracker that:
1. Accepts a natural-language description of exercises done (e.g. "I ran 5km and did push-ups for 20 minutes")
2. Sends it to the Nutritionix Natural Language API to extract exercise name, duration, and calories burned
3. Saves each parsed exercise as a row in a Google Sheet via the Sheety API
4. Secures the Sheety endpoint with HTTP Basic Authentication

## Concepts covered in the original build

- HTTP POST requests with `requests`
- Custom request headers (API key authentication)
- Passing a JSON body to an API (`json=` parameter)
- Parsing JSON responses
- `datetime` for automatic date/time stamping
- `requests.auth.HTTPBasicAuth` for Basic Authentication
- Environment variable pattern (partially — course hardcodes credentials)

## Steps from the course

1. Setup API credentials and create a Google Sheet
2. Query Nutritionix with natural language input
3. Connect the sheet to Sheety and get an endpoint URL
4. POST parsed exercises to the sheet
5. Secure Sheety with Basic Authentication

## Credential note

`original/main.py` contains hardcoded Nutritionix App ID, API key,
Sheety username/password, and a Sheety endpoint URL with a project ID.
These are demo/course credentials from the original exercise session (September 2025).
The advanced build reads all credentials from `.env` via `python-dotenv`.

## Advanced build extensions

- OOP split: `NutritionixClient` handles API fetching, `SheetWriter` handles posting
- All magic numbers and URLs moved to `config.py`
- All credentials loaded from `.env` (no hardcoded secrets)
- `response.raise_for_status()` for proper error surfacing
- `sys.path.insert` pattern for correct imports when launched from `menu.py`
