"""Entry point for the Personal Finance Dashboard application."""

import tkinter as tk
from tkinter import ttk

from budget import create_screen as budget_screen
from dashboard import create_screen as dashboard_screen
from database import initialize_database
from reports import create_screen as report_screen
from transactions import create_screen as transaction_screen


def main():
    """Initialize the database and display the main application window."""
    initialize_database()

    root = tk.Tk()
    root.title("Personal Finance Dashboard")
    root.geometry("900x600")
    root.minsize(800, 500)

    ttk.Label(
        root,
        text="Personal Finance Dashboard",
        font=("Arial", 20, "bold"),
    ).pack(pady=(15, 10))

    navigation = ttk.Frame(root, padding=(10, 0))
    navigation.pack(fill="x")

    content = ttk.Frame(root, padding=10)
    content.pack(fill="both", expand=True)

    screens = {
        "Dashboard": dashboard_screen,
        "Transactions": transaction_screen,
        "Budget": budget_screen,
        "Reports": report_screen,
    }

    def show_screen(screen_name):
        """Replace the current content with the selected module screen."""
        for child in content.winfo_children():
            child.destroy()

        screen = screens[screen_name](content)
        screen.pack(fill="both", expand=True)

    for screen_name in screens:
        ttk.Button(
            navigation,
            text=screen_name,
            command=lambda name=screen_name: show_screen(name),
        ).pack(side="left", padx=5, pady=5)

    show_screen("Dashboard")
    root.mainloop()


if __name__ == "__main__":
    main()
