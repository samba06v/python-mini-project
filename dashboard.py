# dashboard.py
# Member 3: Dashboard and financial calculations
# Shows total income, total expenses, net savings and savings percentage
# for a selected month, using real data from finance.db.

import calendar
import sqlite3
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox

from database import get_connection


# ---------------------------------------------------------------
# BLOCK 1: Financial calculation functions (database queries)
# ---------------------------------------------------------------

def get_total_income(start_date, end_date):
    """Return the sum of all income amounts between two dates (inclusive)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # SUM() adds up the amounts. Parameterized query: ? marks are
        # replaced safely by the values in the tuple.
        cursor.execute(
            "SELECT SUM(amount) FROM transactions "
            "WHERE type = ? AND date BETWEEN ? AND ?",
            ("income", start_date, end_date),
        )
        result = cursor.fetchone()[0]
    finally:
        conn.close()  # always close the connection
    # SUM() returns None when there are no rows, so we return 0.0 instead
    return result if result is not None else 0.0


def get_total_expenses(start_date, end_date):
    """Return the sum of all expense amounts between two dates (inclusive)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT SUM(amount) FROM transactions "
            "WHERE type = ? AND date BETWEEN ? AND ?",
            ("expense", start_date, end_date),
        )
        result = cursor.fetchone()[0]
    finally:
        conn.close()
    return result if result is not None else 0.0


def get_net_savings(start_date, end_date):
    """Net Savings = Total Income - Total Expenses."""
    return get_total_income(start_date, end_date) - get_total_expenses(start_date, end_date)


def get_category_expenses(start_date, end_date):
    """Return a dictionary of expense totals per category.
    Example: {"Food": 5200.0, "Rent": 12000.0}  (largest first)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # GROUP BY gives one row per category with its own SUM
        cursor.execute(
            "SELECT category, SUM(amount) FROM transactions "
            "WHERE type = ? AND date BETWEEN ? AND ? "
            "GROUP BY category ORDER BY SUM(amount) DESC",
            ("expense", start_date, end_date),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()
    return {category: total for category, total in rows}


def get_savings_percentage(total_income, net_savings):
    """Savings % = (Net Savings / Total Income) * 100.
    Returns 0 when income is zero to avoid division by zero."""
    if total_income == 0:
        return 0.0
    return (net_savings / total_income) * 100


# ---------------------------------------------------------------
# BLOCK 2: Helper to convert month and year into a date range
# ---------------------------------------------------------------

def get_month_range(month, year):
    """Return (start_date, end_date) strings in YYYY-MM-DD for a month."""
    last_day = calendar.monthrange(year, month)[1]  # 28, 29, 30 or 31
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{last_day:02d}"
    return start_date, end_date


# ---------------------------------------------------------------
# BLOCK 3: The dashboard screen
# ---------------------------------------------------------------

def create_screen(parent):
    """Build the dashboard inside a Frame and return it to main.py."""
    frame = ttk.Frame(parent, padding=15)

    month_names = list(calendar.month_name)[1:]  # January ... December
    today = date.today()

    # --- Heading ---
    ttk.Label(frame, text="Financial Overview",
              font=("Arial", 18, "bold")).pack(pady=(0, 10))

    # --- Month / year selection and Refresh button ---
    select_frame = ttk.Frame(frame)
    select_frame.pack(pady=5)

    ttk.Label(select_frame, text="Month:").grid(row=0, column=0, padx=5)
    month_var = tk.StringVar(value=month_names[today.month - 1])
    month_box = ttk.Combobox(select_frame, textvariable=month_var,
                             values=month_names, state="readonly", width=12)
    month_box.grid(row=0, column=1, padx=5)

    ttk.Label(select_frame, text="Year:").grid(row=0, column=2, padx=5)
    years = [str(y) for y in range(today.year - 5, today.year + 2)]
    year_var = tk.StringVar(value=str(today.year))
    year_box = ttk.Combobox(select_frame, textvariable=year_var,
                            values=years, state="readonly", width=8)
    year_box.grid(row=0, column=3, padx=5)

    # --- Three summary sections ---
    summary_frame = ttk.Frame(frame)
    summary_frame.pack(pady=15, fill="x")

    income_var = tk.StringVar(value="0.00")
    expense_var = tk.StringVar(value="0.00")
    savings_var = tk.StringVar(value="0.00")
    percent_var = tk.StringVar(value="Savings Percentage: 0.00%")

    def make_card(column, title, variable):
        card = ttk.LabelFrame(summary_frame, text=title, padding=10)
        card.grid(row=0, column=column, padx=8, sticky="nsew")
        summary_frame.columnconfigure(column, weight=1)
        ttk.Label(card, textvariable=variable,
                  font=("Arial", 16, "bold")).pack()

    make_card(0, "Total Income", income_var)
    make_card(1, "Total Expenses", expense_var)
    make_card(2, "Net Savings", savings_var)

    ttk.Label(frame, textvariable=percent_var,
              font=("Arial", 12)).pack(pady=5)

    # --- Category-wise expense table ---
    ttk.Label(frame, text="Expenses by Category",
              font=("Arial", 12, "bold")).pack(pady=(10, 3))
    table = ttk.Treeview(frame, columns=("category", "total"),
                         show="headings", height=6)
    table.heading("category", text="Category")
    table.heading("total", text="Total Spent")
    table.column("category", width=200)
    table.column("total", width=120, anchor="e")
    table.pack(fill="x")

    # --- Refresh logic ---
    def refresh_dashboard():
        """Read month/year, query the database, update all labels."""
        try:
            month = month_names.index(month_var.get()) + 1
            year = int(year_var.get())
            start_date, end_date = get_month_range(month, year)

            total_income = get_total_income(start_date, end_date)
            total_expenses = get_total_expenses(start_date, end_date)
            net_savings = total_income - total_expenses
            percentage = get_savings_percentage(total_income, net_savings)
            categories = get_category_expenses(start_date, end_date)
        except (sqlite3.Error, ValueError) as error:
            messagebox.showerror("Error", f"Could not load dashboard data:\n{error}")
            return

        income_var.set(f"{total_income:.2f}")
        expense_var.set(f"{total_expenses:.2f}")
        savings_var.set(f"{net_savings:.2f}")
        percent_var.set(f"Savings Percentage: {percentage:.2f}%")

        # Clear old rows, then insert the new ones
        for row in table.get_children():
            table.delete(row)
        for category, total in categories.items():
            table.insert("", "end", values=(category, f"{total:.2f}"))

    ttk.Button(select_frame, text="Refresh",
               command=refresh_dashboard).grid(row=0, column=4, padx=10)

    # Update automatically when the month or year changes
    month_box.bind("<<ComboboxSelected>>", lambda event: refresh_dashboard())
    year_box.bind("<<ComboboxSelected>>", lambda event: refresh_dashboard())

    refresh_dashboard()  # show current month's data immediately
    return frame
