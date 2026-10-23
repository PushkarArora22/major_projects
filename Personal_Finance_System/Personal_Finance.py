import csv
import sqlite3
from datetime import datetime

DB_NAME = "finance.db"


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                transaction_date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        """)


def choose_type():
    while True:
        print("1. Income")
        print("2. Expense")
        choice = input("Choose type: ").strip()
        if choice == "1":
            return "Income"
        if choice == "2":
            return "Expense"
        print("Invalid choice.")


def add_transaction():
    transaction_type = choose_type()
    category = input("Category: ").strip()
    amount_text = input("Amount: ").strip()
    date = input("Date (YYYY-MM-DD, blank for today): ").strip()
    description = input("Description: ").strip()

    try:
        amount = float(amount_text)
        if amount < 0:
            raise ValueError
    except ValueError:
        print("Enter a valid non-negative amount.")
        return

    if not category:
        print("Category is required.")
        return

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date.")
        return

    with connect() as conn:
        conn.execute("""
            INSERT INTO transactions
            (transaction_type, category, amount, transaction_date, description)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_type, category, amount, date, description))

    print("Transaction added successfully.")


def list_transactions():
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, transaction_type, category, amount,
                   transaction_date, description
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """).fetchall()

    if not rows:
        print("No transactions found.")
        return

    for row in rows:
        print(" | ".join(str(value) for value in row))


def monthly_summary():
    month = input("Enter month (YYYY-MM): ").strip()
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month.")
        return

    with connect() as conn:
        income = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Income'
              AND transaction_date LIKE ?
        """, (f"{month}%",)).fetchone()[0]

        expenses = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Expense'
              AND transaction_date LIKE ?
        """, (f"{month}%",)).fetchone()[0]

    print(f"Income: ₹{income:.2f}")
    print(f"Expenses: ₹{expenses:.2f}")
    print(f"Balance: ₹{income - expenses:.2f}")


def category_summary():
    with connect() as conn:
        rows = conn.execute("""
            SELECT category, SUM(amount)
            FROM transactions
            WHERE transaction_type = 'Expense'
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()

    for category, amount in rows:
        print(f"{category}: ₹{amount:.2f}")


def export_csv():
    filename = input("CSV filename [transactions.csv]: ").strip() or "transactions.csv"

    with connect() as conn:
        rows = conn.execute("""
            SELECT id, transaction_type, category, amount,
                   transaction_date, description
            FROM transactions
            ORDER BY transaction_date
        """).fetchall()

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "id", "transaction_type", "category",
            "amount", "transaction_date", "description"
        ])
        writer.writerows(rows)

    print(f"Exported {len(rows)} transactions to {filename}.")


def main():
    init_db()
    while True:
        print("""
========= PERSONAL FINANCE MANAGER =========
1. Add transaction
2. List transactions
3. Monthly summary
4. Expense by category
5. Export to CSV
6. Exit
=============================================
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            list_transactions()
        elif choice == "3":
            monthly_summary()
        elif choice == "4":
            category_summary()
        elif choice == "5":
            export_csv()
        elif choice == "6":
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

