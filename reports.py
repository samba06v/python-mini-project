# reports.py
# Member 4: Financial Reports screen (monthly and yearly)
#
# This module provides create_screen(parent), which builds a Frame that shows
# total income, total expenses, net savings, savings % and category-wise expenses.

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import get_connection, initialize_database

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ---------------------------------------------------------------------------
# DATABASE HELPER (no GUI code here)
# ---------------------------------------------------------------------------

def get_report_data(date_prefix):
    """
    Return (total_income, total_expenses, category_rows) for a period.

    date_prefix is "YYYY-MM" for a monthly report or "YYYY" for a yearly one.
    Dates are stored as YYYY-MM-DD, so LIKE 'prefix%' picks the right rows.
    """
    pattern = date_prefix + "%"

    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Totals for income and expense in one query
        cursor.execute(
            "SELECT type, SUM(amount) FROM transactions "
            "WHERE date LIKE ? GROUP BY type",
            (pattern,),
        )
        totals = dict(cursor.fetchall())
        total_income = totals.get("income") or 0.0
        total_expenses = totals.get("expense") or 0.0

        # Expenses grouped by category, biggest first
        cursor.execute(
            "SELECT category, SUM(amount) FROM transactions "
            "WHERE type = 'expense' AND date LIKE ? "
            "GROUP BY category ORDER BY SUM(amount) DESC",
            (pattern,),
        )
        category_rows = cursor.fetchall()
    finally:
        conn.close()

    return total_income, total_expenses, category_rows


# ---------------------------------------------------------------------------
# SCREEN
# ---------------------------------------------------------------------------

def create_screen(parent):
    """Build the reports screen inside a new Frame and return that Frame."""
    initialize_database()  # makes sure the tables exist (safe to call again)

    frame = tk.Frame(parent)

    tk.Label(frame, text="Financial Reports",
             font=("Arial", 16, "bold")).pack(pady=10)

    today = date.today()
    year_values = [str(y) for y in range(today.year - 5, today.year + 6)]

    # ----- Report options -----
    options = tk.Frame(frame)
    options.pack(pady=5)

    report_type = tk.StringVar(value="monthly")

    def update_month_state():
        """The month dropdown is only needed for the monthly report."""
        if report_type.get() == "monthly":
            month_box.config(state="readonly")
        else:
            month_box.config(state="disabled")

    ttk.Radiobutton(options, text="Monthly Report", variable=report_type,
                    value="monthly", command=update_month_state).grid(row=0, column=0, padx=10, pady=5)
    ttk.Radiobutton(options, text="Yearly Report", variable=report_type,
                    value="yearly", command=update_month_state).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(options, text="Month:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    month_box = ttk.Combobox(options, values=MONTH_NAMES, state="readonly", width=15)
    month_box.current(today.month - 1)
    month_box.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(options, text="Year:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    year_box = ttk.Combobox(options, values=year_values, state="readonly", width=10)
    year_box.set(str(today.year))
    year_box.grid(row=1, column=3, padx=5, pady=5)

    # ----- Summary section -----
    summary = ttk.LabelFrame(frame, text="Summary")
    summary.pack(padx=10, pady=10, fill="x")

    period_text = tk.StringVar(value="")
    income_text = tk.StringVar(value="0.00")
    expense_text = tk.StringVar(value="0.00")
    savings_text = tk.StringVar(value="0.00")
    percent_text = tk.StringVar(value="N/A")

    tk.Label(summary, textvariable=period_text,
             font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

    summary_items = [
        ("Total Income:", income_text),
        ("Total Expenses:", expense_text),
        ("Net Savings:", savings_text),
        ("Savings Percentage:", percent_text),
    ]
    for row_number, (label_text, variable) in enumerate(summary_items, start=1):
        tk.Label(summary, text=label_text, anchor="w", width=20).grid(
            row=row_number, column=0, padx=10, pady=2, sticky="w")
        tk.Label(summary, textvariable=variable, anchor="w", width=20).grid(
            row=row_number, column=1, padx=10, pady=2, sticky="w")

    # ----- Category table -----
    columns = ("Category", "Amount Spent", "% of Expenses")
    table = ttk.Treeview(frame, columns=columns, show="headings", height=8)
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=160, anchor="center")

    # ----- Generate the report -----
    def generate_report(show_empty_message=True):
        """Read the selected period, query the database and fill the screen."""
        year = int(year_box.get())

        if report_type.get() == "monthly":
            month = MONTH_NAMES.index(month_box.get()) + 1
            date_prefix = f"{year:04d}-{month:02d}"
            period_text.set(f"Report for {MONTH_NAMES[month - 1]} {year}")
        else:
            date_prefix = f"{year:04d}"
            period_text.set(f"Report for the year {year}")

        try:
            total_income, total_expenses, category_rows = get_report_data(date_prefix)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not create report:\n{error}")
            return

        net_savings = total_income - total_expenses

        income_text.set(f"{total_income:.2f}")
        expense_text.set(f"{total_expenses:.2f}")
        savings_text.set(f"{net_savings:.2f}")

        # Savings % = net savings / income * 100 (cannot divide when income is 0)
        if total_income > 0:
            percent_text.set(f"{net_savings / total_income * 100:.1f}%")
        else:
            percent_text.set("N/A (no income)")

        # Refill the category-wise expense table
        for item in table.get_children():
            table.delete(item)
        for category, amount in category_rows:
            if total_expenses > 0:
                share = f"{amount / total_expenses * 100:.1f}%"
            else:
                share = "0.0%"
            table.insert("", "end", values=(category, f"{amount:.2f}", share))

        if show_empty_message and total_income == 0 and total_expenses == 0:
            messagebox.showinfo("No Data", "No transactions found for this period.")

    ttk.Button(frame, text="Generate Report", command=generate_report).pack(pady=5)
    table.pack(padx=10, pady=5, fill="both", expand=True)

    generate_report(show_empty_message=False)  # show the current month on open
    return frame
