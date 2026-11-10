# budget.py
# Member 4: Monthly Budget Management screen
#
# This module provides create_screen(parent), which builds a Frame that lets the
# user set a monthly budget per expense category and see how much has been spent.

import math
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import get_connection, initialize_database
from config import EXPENSE_CATEGORIES

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ---------------------------------------------------------------------------
# DATABASE / CALCULATION HELPERS (no GUI code here)
# ---------------------------------------------------------------------------

def get_status(budget_amount, spent):
    """Return (status_text, percent_used) for one category."""
    if budget_amount <= 0:
        return "Normal", 0.0

    percent_used = spent / budget_amount * 100

    if percent_used >= 100:
        status = "Budget Exceeded"
    elif percent_used >= 80:
        status = "Approaching Budget"
    else:
        status = "Normal"
    return status, percent_used


def get_spent(cursor, category, month, year):
    """Total expenses of one category in the given month and year."""
    # Dates are stored as YYYY-MM-DD, so the first 7 characters are YYYY-MM
    month_text = f"{year:04d}-{month:02d}"
    cursor.execute(
        "SELECT SUM(amount) FROM transactions "
        "WHERE type = 'expense' AND category = ? AND substr(date, 1, 7) = ?",
        (category, month_text),
    )
    total = cursor.fetchone()[0]
    return total if total is not None else 0.0  # SUM gives None when no rows


def get_budget_rows(month, year):
    """Return one tuple per budget: (category, budget, spent, remaining, status, percent)."""
    rows = []
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, amount FROM budgets "
            "WHERE month = ? AND year = ? ORDER BY category",
            (month, year),
        )
        budgets = cursor.fetchall()

        for category, budget_amount in budgets:
            spent = get_spent(cursor, category, month, year)
            remaining = budget_amount - spent
            status, percent = get_status(budget_amount, spent)
            rows.append((category, budget_amount, spent, remaining, status, percent))
    finally:
        conn.close()
    return rows


def save_budget(category, amount, month, year):
    """Insert a new budget or update the existing one. Returns 'added' or 'updated'."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM budgets WHERE category = ? AND month = ? AND year = ?",
            (category, month, year),
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE budgets SET amount = ? WHERE id = ?", (amount, existing[0])
            )
            result = "updated"
        else:
            cursor.execute(
                "INSERT INTO budgets (category, amount, month, year) VALUES (?, ?, ?, ?)",
                (category, amount, month, year),
            )
            result = "added"
        conn.commit()
    finally:
        conn.close()
    return result


# ---------------------------------------------------------------------------
# SCREEN
# ---------------------------------------------------------------------------

def create_screen(parent):
    """Build the budget screen inside a new Frame and return that Frame."""
    initialize_database()  # makes sure the tables exist (safe to call again)

    frame = tk.Frame(parent)

    tk.Label(frame, text="Monthly Budget Management",
             font=("Arial", 16, "bold")).pack(pady=10)

    # ----- Input form -----
    form = tk.Frame(frame)
    form.pack(pady=5)

    today = date.today()
    year_values = [str(y) for y in range(today.year - 5, today.year + 6)]

    tk.Label(form, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    category_box = ttk.Combobox(form, values=EXPENSE_CATEGORIES,
                                state="readonly", width=18)
    category_box.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form, text="Budget Amount:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    amount_entry = ttk.Entry(form, width=20)
    amount_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(form, text="Month:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    month_box = ttk.Combobox(form, values=MONTH_NAMES, state="readonly", width=18)
    month_box.current(today.month - 1)  # default: current month
    month_box.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form, text="Year:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
    year_box = ttk.Combobox(form, values=year_values, state="readonly", width=18)
    year_box.set(str(today.year))  # default: current year
    year_box.grid(row=1, column=3, padx=5, pady=5)

    # ----- Table -----
    columns = ("Category", "Budget Amount", "Amount Spent", "Remaining Amount", "Status")
    table = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=140, anchor="center")

    # Row colours so the status is easy to notice
    table.tag_configure("Normal", background="#e6f4ea")
    table.tag_configure("Approaching Budget", background="#fff4cc")
    table.tag_configure("Budget Exceeded", background="#f8d7da")

    # ----- Functions that use the widgets above -----
    def get_selected_period():
        """Return (month_number, year_number) from the two dropdowns."""
        month = MONTH_NAMES.index(month_box.get()) + 1
        year = int(year_box.get())
        return month, year

    def load_table():
        """Refill the table with the budgets of the selected month. Returns the rows."""
        month, year = get_selected_period()
        for item in table.get_children():
            table.delete(item)

        try:
            rows = get_budget_rows(month, year)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not load budgets:\n{error}")
            return []

        for category, budget, spent, remaining, status, percent in rows:
            table.insert(
                "", "end",
                values=(category, f"{budget:.2f}", f"{spent:.2f}",
                        f"{remaining:.2f}", status),
                tags=(status,),
            )
        return rows

    def on_save():
        """Validate the form, save the budget, then warn if needed."""
        category = category_box.get()
        if category == "":
            messagebox.showerror("Error", "Please select a category.")
            return

        try:
            amount = float(amount_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Budget amount must be a number.")
            return
        if not math.isfinite(amount) or amount <= 0:
            messagebox.showerror("Error", "Budget amount must be greater than 0.")
            return

        month, year = get_selected_period()
        try:
            result = save_budget(category, amount, month, year)
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", f"Could not save budget:\n{error}")
            return

        amount_entry.delete(0, tk.END)
        rows = load_table()

        message = f"Budget for {category} ({MONTH_NAMES[month - 1]} {year}) {result}."

        # Look up the saved category to see whether it needs a warning
        for row_category, budget, spent, remaining, status, percent in rows:
            if row_category == category and status != "Normal":
                message += (f"\n\nWarning: {status}!\n"
                            f"Spent {spent:.2f} of {budget:.2f} ({percent:.0f}%).")
                messagebox.showwarning("Budget Warning", message)
                return
        messagebox.showinfo("Success", message)

    def on_refresh():
        """Reload the table and show one warning listing all problem categories."""
        rows = load_table()
        warnings = []
        for category, budget, spent, remaining, status, percent in rows:
            if status != "Normal":
                warnings.append(f"{category}: {status} ({percent:.0f}% used)")
        if warnings:
            messagebox.showwarning("Budget Warning", "\n".join(warnings))

    def on_row_select(event):
        """Copy the selected row into the form so the budget can be updated."""
        selected = table.selection()
        if not selected:
            return
        values = table.item(selected[0], "values")
        category_box.set(values[0])
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, values[1])

    # ----- Buttons -----
    button_row = tk.Frame(frame)
    button_row.pack(pady=8)
    ttk.Button(button_row, text="Save / Update Budget", command=on_save).pack(side="left", padx=5)
    ttk.Button(button_row, text="Refresh", command=on_refresh).pack(side="left", padx=5)

    table.pack(padx=10, pady=5, fill="both", expand=True)

    # ----- Events -----
    month_box.bind("<<ComboboxSelected>>", lambda event: load_table())
    year_box.bind("<<ComboboxSelected>>", lambda event: load_table())
    table.bind("<<TreeviewSelect>>", on_row_select)

    load_table()  # show the current month when the screen opens
    return frame
