
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import math

from database import get_connection
from config import CATEGORIES


# =====================================================
# 1. DATABASE FUNCTIONS
# =====================================================

# Add a new transaction to the database
def add_transaction(data):

    data = validate_transaction_data(data)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO transactions
            (type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["type"],
            data["amount"],
            data["category"],
            data["description"],
            data["date"]
        ))

        conn.commit()

    finally:
        conn.close()


# Get all transactions from the database
def get_transactions():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, type, amount, category, description, date
            FROM transactions
            ORDER BY date DESC, id DESC
        """)

        rows = cursor.fetchall()

        # Convert database rows into dictionaries
        transactions = []

        for row in rows:
            transactions.append({
                "id": row[0],
                "type": row[1],
                "amount": row[2],
                "category": row[3],
                "description": row[4],
                "date": row[5]
            })

        return transactions

    finally:
        conn.close()


# Update an existing transaction
def update_transaction(transaction_id, data):

    data = validate_transaction_data(data)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE transactions
            SET type = ?, amount = ?, category = ?,
                description = ?, date = ?
            WHERE id = ?
        """, (
            data["type"],
            data["amount"],
            data["category"],
            data["description"],
            data["date"],
            transaction_id
        ))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# Delete a transaction
def delete_transaction(transaction_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        conn.commit()

        return cursor.rowcount > 0

    finally:
        conn.close()


# Search transactions by category or description
def search_transactions(keyword):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        search_value = "%" + keyword.strip() + "%"

        cursor.execute("""
            SELECT id, type, amount, category, description, date
            FROM transactions
            WHERE category LIKE ? OR description LIKE ?
            ORDER BY date DESC, id DESC
        """, (search_value, search_value))

        rows = cursor.fetchall()

        transactions = []

        for row in rows:
            transactions.append({
                "id": row[0],
                "type": row[1],
                "amount": row[2],
                "category": row[3],
                "description": row[4],
                "date": row[5]
            })

        return transactions

    finally:
        conn.close()


# =====================================================
# 2. INPUT VALIDATION
# =====================================================

def validate_transaction_data(data):

    transaction_type = str(data["type"]).strip().lower()
    category = str(data["category"]).strip()
    description = str(data["description"]).strip()
    date = str(data["date"]).strip()

    if transaction_type not in ("income", "expense"):
        raise ValueError("Select Income or Expense.")

    try:
        amount = float(data["amount"])
    except (ValueError, TypeError):
        raise ValueError("Please enter a valid amount.")

    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if not category:
        raise ValueError("Please select a category.")

    if not description:
        raise ValueError("Please enter a description.")

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        if parsed_date.strftime("%Y-%m-%d") != date:
            raise ValueError()

    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    return {
        "type": transaction_type,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }


# =====================================================
# 3. GUI SCREEN
# =====================================================

def create_screen(parent):

    # Main frame
    frame = ttk.Frame(parent, padding=15)

    # Store selected transaction ID
    selected_id = {"value": None}

    # -----------------------------
    # TITLE
    # -----------------------------

    title = ttk.Label(
        frame,
        text="Transaction Management",
        font=("Arial", 18, "bold")
    )
    title.pack(pady=10)

    # -----------------------------
    # INPUT SECTION
    # -----------------------------

    input_frame = ttk.LabelFrame(
        frame,
        text="Add / Update Transaction",
        padding=10
    )
    input_frame.pack(fill="x", pady=10)

    # Transaction Type
    ttk.Label(input_frame, text="Transaction Type").grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )

    type_var = tk.StringVar(value="Income")

    type_combo = ttk.Combobox(
        input_frame,
        textvariable=type_var,
        values=["Income", "Expense"],
        state="readonly",
        width=18
    )
    type_combo.grid(row=0, column=1, padx=5, pady=5)

    # Amount
    ttk.Label(input_frame, text="Amount").grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )

    amount_entry = ttk.Entry(input_frame, width=20)
    amount_entry.grid(row=0, column=3, padx=5, pady=5)

    # Category
    ttk.Label(input_frame, text="Category").grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )

    category_var = tk.StringVar()

    category_combo = ttk.Combobox(
        input_frame,
        textvariable=category_var,
        values=CATEGORIES,
        state="readonly",
        width=18
    )
    category_combo.grid(row=1, column=1, padx=5, pady=5)

    if CATEGORIES:
        category_combo.current(0)

    # Description
    ttk.Label(input_frame, text="Description").grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )

    description_entry = ttk.Entry(input_frame, width=20)
    description_entry.grid(row=1, column=3, padx=5, pady=5)

    # Date
    ttk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(
        row=2, column=0, padx=5, pady=5, sticky="w"
    )

    date_entry = ttk.Entry(input_frame, width=20)
    date_entry.grid(row=2, column=1, padx=5, pady=5)

    date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    # -----------------------------
    # CLEAR INPUT FUNCTION
    # -----------------------------

    def clear_fields():

        selected_id["value"] = None

        type_var.set("Income")
        amount_entry.delete(0, tk.END)

        if CATEGORIES:
            category_combo.current(0)
        else:
            category_var.set("")

        description_entry.delete(0, tk.END)

        date_entry.delete(0, tk.END)
        date_entry.insert(
            0, datetime.today().strftime("%Y-%m-%d")
        )

        transaction_table.selection_remove(
            transaction_table.selection()
        )

    # -----------------------------
    # GET INPUT DATA
    # -----------------------------

    def get_form_data():

        return {
            "type": type_var.get(),
            "amount": amount_entry.get(),
            "category": category_var.get(),
            "description": description_entry.get(),
            "date": date_entry.get()
        }

    # -----------------------------
    # TRANSACTION TABLE
    # -----------------------------

    table_frame = ttk.LabelFrame(
        frame,
        text="All Transactions",
        padding=10
    )
    table_frame.pack(fill="both", expand=True, pady=10)

    columns = (
        "ID",
        "Type",
        "Amount",
        "Category",
        "Description",
        "Date"
    )

    transaction_table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=10
    )

    # Column headings
    for column in columns:
        transaction_table.heading(
            column,
            text=column
        )

    transaction_table.column("ID", width=45, anchor="center")
    transaction_table.column("Type", width=85, anchor="center")
    transaction_table.column("Amount", width=90, anchor="center")
    transaction_table.column("Category", width=110)
    transaction_table.column("Description", width=180)
    transaction_table.column("Date", width=105, anchor="center")

    # Scrollbars
    vertical_scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=transaction_table.yview
    )

    horizontal_scroll = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=transaction_table.xview
    )

    transaction_table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    transaction_table.grid(row=0, column=0, sticky="nsew")
    vertical_scroll.grid(row=0, column=1, sticky="ns")
    horizontal_scroll.grid(row=1, column=0, sticky="ew")

    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    # -----------------------------
    # REFRESH TABLE FUNCTION
    # -----------------------------

    def refresh_table(keyword=None):

        for item in transaction_table.get_children():
            transaction_table.delete(item)

        if keyword is None:
            records = get_transactions()
        else:
            records = search_transactions(keyword)

        for record in records:

            transaction_table.insert(
                "",
                tk.END,
                iid=str(record["id"]),
                values=(
                    record["id"],
                    record["type"].capitalize(),
                    f'{record["amount"]:.2f}',
                    record["category"],
                    record["description"],
                    record["date"]
                )
            )

    # -----------------------------
    # ADD TRANSACTION BUTTON
    # -----------------------------

    def handle_add():

        try:
            data = get_form_data()

            add_transaction(data)

            messagebox.showinfo(
                "Success",
                "Transaction added successfully!",
                parent=frame
            )

            clear_fields()
            refresh_table()

        except ValueError as error:

            messagebox.showerror(
                "Invalid Input",
                str(error),
                parent=frame
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=frame
            )

    # -----------------------------
    # SELECT TRANSACTION
    # -----------------------------

    def load_selected(event=None):

        selected = transaction_table.selection()

        if not selected:
            return

        transaction_id = int(selected[0])

        values = transaction_table.item(
            selected[0], "values"
        )

        selected_id["value"] = transaction_id

        type_var.set(values[1])
        
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, values[2])

        category_var.set(values[3])

        description_entry.delete(0, tk.END)
        description_entry.insert(0, values[4])

        date_entry.delete(0, tk.END)
        date_entry.insert(0, values[5])

    transaction_table.bind(
        "<<TreeviewSelect>>",
        load_selected
    )

    # -----------------------------
    # UPDATE TRANSACTION BUTTON
    # -----------------------------

    def handle_update():

        if selected_id["value"] is None:
            messagebox.showwarning(
                "Warning",
                "Please select a transaction first.",
                parent=frame
            )
            return

        try:
            data = get_form_data()

            updated = update_transaction(
                selected_id["value"],
                data
            )

            if updated:
                messagebox.showinfo(
                    "Success",
                    "Transaction updated successfully!",
                    parent=frame
                )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Transaction not found.",
                    parent=frame
                )

            clear_fields()
            refresh_table()

        except ValueError as error:

            messagebox.showerror(
                "Invalid Input",
                str(error),
                parent=frame
            )

        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=frame
            )

    # -----------------------------
    # DELETE TRANSACTION BUTTON
    # -----------------------------

    def handle_delete():

        if selected_id["value"] is None:
            messagebox.showwarning(
                "Warning",
                "Please select a transaction first.",
                parent=frame
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            parent=frame
        )

        if confirm:

            try:
                deleted = delete_transaction(
                    selected_id["value"]
                )

                if deleted:
                    messagebox.showinfo(
                        "Success",
                        "Transaction deleted successfully!",
                        parent=frame
                    )
                else:
                    messagebox.showwarning(
                        "Warning",
                        "Transaction not found.",
                        parent=frame
                    )

                clear_fields()
                refresh_table()

            except Exception as error:

                messagebox.showerror(
                    "Database Error",
                    str(error),
                    parent=frame
                )

    # -----------------------------
    # SEARCH TRANSACTIONS
    # -----------------------------

    search_frame = ttk.Frame(frame)
    search_frame.pack(fill="x", pady=5)

    ttk.Label(
        search_frame,
        text="Search Category / Description:"
    ).pack(side="left", padx=5)

    search_entry = ttk.Entry(
        search_frame,
        width=25
    )
    search_entry.pack(side="left", padx=5)

    def handle_search():

        keyword = search_entry.get()
        refresh_table(keyword)

    def clear_search():

        search_entry.delete(0, tk.END)
        refresh_table()

    ttk.Button(
        search_frame,
        text="Search",
        command=handle_search
    ).pack(side="left", padx=5)

    ttk.Button(
        search_frame,
        text="Show All",
        command=clear_search
    ).pack(side="left", padx=5)

    # -----------------------------
    # ACTION BUTTONS
    # -----------------------------

    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    ttk.Button(
        button_frame,
        text="Add Transaction",
        command=handle_add
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Update Transaction",
        command=handle_update
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Delete Transaction",
        command=handle_delete
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Clear Fields",
        command=clear_fields
    ).pack(side="left", padx=5)

    # Load existing transactions when screen opens
    try:
        refresh_table()
    except Exception as error:
        messagebox.showerror(
            "Database Error",
            str(error),
            parent=frame
        )

    return frame
