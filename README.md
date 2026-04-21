# 💰 Smart Budget Advisor

**Smart Budget Advisor** is a personal finance web application built with **Flask** that helps users track expenses, analyze spending patterns, and receive AI-assisted insights — all in a simple, privacy-focused setup using local JSON storage.

The project was designed as a **full-stack portfolio application** with emphasis on:
- clean backend architecture
- correct financial and currency logic
- user data isolation
- realistic, production-style features

---

## 🚀 Features

### 💸 Expense Management
- Add, edit and delete expenses
- Assign categories and descriptions
- Per-user expense isolation
- Input validation and error handling

### 🌍 Currency Support
- User-selectable default currency (PLN, EUR, GBP, etc.)
- Automatic currency conversion based on real exchange rates
- Exchange rates fetched from a free external API and cached daily
- All expenses internally stored using a base currency to ensure data consistency

### 📊 Dashboard & Analytics
- Expense overview for the logged-in user
- Filtering by category
- Filtering by date range
- Empty-state handling and safe edge cases
- Bar chart and pie chart visualizations of spending

### 🤖 AI Advisor
- Dedicated **Advisor** page with:
  - Key spending insights
  - Basic statistics (average transaction, median transaction)
  - Monthly spending trends
  - Category breakdown
  - Simple anomaly detection
- AI chat assistant for budget-related questions
- Export advisor insights and statistics to a PDF report

### 📁 Data Export
- Export expenses to CSV
- Export charts as image files
- Export full financial analysis to PDF

### 👤 Authentication
- User registration and login
- Secure password hashing
- Session-based authentication
- Logout functionality
- User-specific settings and data separation

### ⚙️ User Settings
- Settings panel available from the navbar
- Change default display currency
- Preferences stored per user

---

## 🧠 Technical Overview

### Backend
- **Python**
- **Flask**
- **Jinja2** templates
- Modular route and logic structure
- JSON-based persistence (no database)

### Currency Conversion
- Real exchange rates fetched from an external API
- Local caching of rates for 24 hours
- Server-side currency conversion (no JavaScript dependency)

### AI Integration
- External AI API used for advisory features
- API keys stored securely via environment variables
- Graceful handling of missing or failed API responses

### Testing
- Unit tests written using **pytest**
- Coverage includes:
  - currency conversion logic
  - application routes and basic app health

---

## 📦 Project Structure (Simplified)
```
smart-budget-advisor/
├── app/
│ ├── routes.py
│ ├── models.py
│ ├── currency.py
│ ├── ai.py
│ ├── templates/
│ └── static/
├── data/
│ ├── data.json
│ ├── users.json
│ └── exchange_rates.json
├── tests/
│ ├── test_currency.py
│ └── test_routes.py
├── requirements.txt
├── app.py
└── README.md
```
---

## 🔐 Environment Variables
Create a .env file in the project root:
```
APP_SECRET_KEY=your_secret_key
GROQ_API_KEY=your_api_key
```
The .env file is excluded from version control.

---

## ▶️ Running the Project Locally
```
pip install -r requirements.txt
flask run
```
Then open:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Tests
```
pytest
```

---

## 🎯 Project Goals
- Build a realistic full-stack Flask application
- Practice backend-driven data validation and processing
- Implement correct and safe currency conversion logic
- Create a portfolio-ready project suitable for recruiters
- Prepare the codebase for future migration to FastAPI or a SQL database

---

## 📌 Notes
- This project intentionally avoids heavy JavaScript usage
- All critical logic (currency conversion, analytics, filtering) is handled server-side
- Designed with clarity and maintainability in mind

---

## 📜 License
This project was created for educational and portfolio purposes.

---