# Personal Finance Dashboard

A beginner-friendly desktop application for recording personal income and expenses, managing monthly budgets, and reviewing financial summaries. It is built with Python, Tkinter, and SQLite.

## Features

- **Dashboard:** View monthly income, expenses, net savings, savings percentage, and expense totals by category.
- **Transactions:** Add, view, search, update, and delete income and expense records.
- **Budgets:** Set or update monthly budgets by expense category and compare budgets with actual spending.
- **Reports:** Generate monthly or yearly summaries, including category-wise expenses.
- **Local storage:** Transaction and budget data is stored in `finance.db` in the project folder.

## Requirements

- Python 3
- Tkinter (included with most standard Python installations)

The application uses Python's built-in `sqlite3` module. No web server, external database, or third-party packages are required.

## Run the application

Open a terminal in the project folder and run:

```powershell
python main.py
```

On Windows, if `python` is not recognized, try:

```powershell
py main.py
```

To get the project from GitHub and run it:

```powershell
git clone https://github.com/samba06v/python-mini-project.git
cd python-mini-project
python main.py
```

The app opens as a desktop window; it does not run at a localhost URL. The `finance.db` file and required tables are created automatically when the app starts.

## Using the application

Use the buttons at the top to switch between Dashboard, Transactions, Budget, and Reports. Enter transactions with a positive amount and a date in `YYYY-MM-DD` format. The dashboard, budget screen, and reports use the saved transactions to calculate totals.

## Project files

| File | Purpose |
| --- | --- |
| `main.py` | Creates the main Tkinter window, navigation, and screen area. |
| `database.py` | Provides the shared SQLite connection and initializes the database tables. |
| `config.py` | Defines the shared income and expense categories. |
| `transactions.py` | Provides transaction entry, search, editing, deletion, and listing. |
| `dashboard.py` | Displays monthly totals, savings, and category expense totals. |
| `budget.py` | Saves monthly category budgets and compares them with spending. |
| `reports.py` | Displays monthly and yearly financial reports. |
| `finance.db` | Created on first launch; stores transactions and budgets. |

## Database tables

The application initializes these tables if they do not already exist:

- `transactions`: `id`, `type`, `amount`, `category`, `description`, `date`
- `budgets`: `id`, `category`, `amount`, `month`, `year`

Existing records are retained when the application initializes the database again.
