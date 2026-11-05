# Expense Tracker

A lightweight internal web app for employees to log, categorize, and track business expenses.

## Features
- Add expenses with submitter name, amount, category, date, and description
- Filter and search expense history
- Live spending summary by category (bar chart)
- Summary stats: total spend, entry count, top category, this month's spend
- Delete entries
- Persistent SQLite storage

## Running Locally

```bash
pip install -r requirements.txt
python app.py
```

App will be available at http://localhost:8080

## Docker

```bash
docker build -t expense-tracker .
docker run -p 8080:8080 -v expenses_data:/data expense-tracker
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `/data/expenses.db` | Path to the SQLite database file |
