"""Common category choices shared by the project screens."""

INCOME_CATEGORIES = [
    "Salary",
    "Business",
    "Freelancing",
    "Investments",
    "Other",
]

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Education",
    "Housing",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Other",
]

# transactions.py uses a single dropdown for all category choices.
CATEGORIES = INCOME_CATEGORIES + [
    category for category in EXPENSE_CATEGORIES
    if category not in INCOME_CATEGORIES
]
