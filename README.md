
# 🏋️ Workout Tracker using Nutritionix + Google Sheets

Track your workouts using natural language input and log the results directly to a Google Sheet — no manual typing required!

This project uses:
- **Nutritionix API** to interpret plain-English workout input (e.g., “I ran 3 miles and did yoga”)
- **Sheety API** to save the parsed workout data into a **Google Sheet**
- **Python** to connect everything and automate the process

---

## 🐍 Python Version

- ✅ **Developed with Python 3.12.9**
- ⚠️ Compatible with **Python 3.10+**
- 📦 Install dependencies via `requirements.txt`

---
## 📸 Demo

You will be prompted by the program to provide exercise info, please give the type of exercise you did and the amount of time you did it for, example: 

> Tell me which exercises you did:  
`I ran 5km and did push-ups for 20 minutes`

✅ **Logs saved to your Google Sheet:**

| Date       | Time     | Exercise  | Duration (minutes) | Calories |
|------------|----------|-----------|---------------------|----------|
| 18/09/2025 | 13:45:22 | Running   | 30                  | 301.22   |
| 18/09/2025 | 13:45:22 | Push-Ups  | 20                  | 115.00   |


---

## 🧠 Features

- 💬 Input workout descriptions in **natural language**
- 🧮 Automatically calculates:
  - Duration
  - Calories burned
- 📅 Logs date and time automatically
- 📄 Saves results to a Google Sheet
- 🔐 Uses **Basic Auth** for secure Sheety access

---

## 🔧 Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/workout-tracker.git
cd workout-tracker
```

### 2. Create a `.env` File

Duplicate the provided example:

```bash
cp .env.example .env
```

Then edit `.env` and add your credentials:

```
APP_ID=your_nutritionix_app_id
API_KEY=your_nutritionix_api_key
SHEETY_USERNAME=your_sheety_username
SHEETY_PASSWORD=your_sheety_password
SHEET_ENDPOINT=https://api.sheety.co/your_project/your_sheet
```

> 🔒 Be sure to add `.env` to `.gitignore` to keep it private.

---

## 🔗 API Setup

### Nutritionix (Natural Language Parser)

1. Go to [Nutritionix Developer Portal](https://developer.nutritionix.com/)
2. Create an account
3. Create a new app to get your **App ID** and **API Key**

### Sheety (Google Sheets API Wrapper)

1. Go to [Sheety](https://sheety.co/)
2. Log in with Google
3. Create a new project linked to a Google Sheet
4. Copy the generated API endpoint and paste into `.env`

---

## 📦 Dependencies

- `requests`
- `python-dotenv` (if using `.env` file to load secrets)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python main.py
```

Then enter your workout description:

```
Tell me which exercises you did: I cycled for 45 minutes and did yoga
```

---

## 📁 Project Structure

```
workout-tracker/
├── main.py             # Main program logic
├── .env.example        # Sample credentials file
├── README.md           # You are here!
└── requirements.txt    # Dependencies list
```

---

## ✅ Sample Google Sheet

| Date       | Time     | Exercise   | Duration (minutes) | Calories |
|------------|----------|------------|---------------------|----------|
| 18/09/2025 | 13:45:22 | Cycling    | 45                  | 412.34   |
| 18/09/2025 | 13:45:22 | Yoga       | 30                  | 140.00   |

---

## 📌 Notes

- The column `"Duration (minutes)"` must **exactly match** the field name in the code and Google Sheet.
- Nutritionix will estimate duration and calories for some workouts if only distance or type is provided.
- You can change your weight, height, age, or gender in the variables at the top of `main.py`.

---

## 📜 License

This project is open-source and free to use for educational purposes.

---

## ✍️ Author

Made by **Xavier O.C.** as part of the 100 Days of Code journey.  
Connect on [LinkedIn](https://www.linkedin.com/in/xavier-ocon-capdeville/)
