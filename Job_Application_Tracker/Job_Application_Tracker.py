import sqlite3
from datetime import datetime

DB_NAME = "job_tracker.db"
STATUSES = ("Applied", "Assessment", "Interview", "Offer", "Rejected")


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                status TEXT NOT NULL,
                application_date TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)


def choose_status():
    for i, status in enumerate(STATUSES, 1):
        print(f"{i}. {status}")
    while True:
        choice = input("Choose status: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(STATUSES):
            return STATUSES[int(choice) - 1]
        print("Invalid choice.")


def add_application():
    company = input("Company: ").strip()
    role = input("Role: ").strip()
    location = input("Location: ").strip()
    status = choose_status()
    notes = input("Notes: ").strip()

    if not company or not role:
        print("Company and role are required.")
        return

    with connect() as conn:
        conn.execute("""
            INSERT INTO applications
            (company, role, location, status, application_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company, role, location, status,
              datetime.now().strftime("%Y-%m-%d"), notes))
    print("Application added successfully.")


def list_applications():
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, company, role, location, status, application_date
            FROM applications
            ORDER BY application_date DESC, id DESC
        """).fetchall()

    if not rows:
        print("No applications found.")
        return

    print("\nID | Company | Role | Location | Status | Date")
    print("-" * 80)
    for row in rows:
        print(" | ".join(str(value) for value in row))


def search_applications():
    term = input("Search company or role: ").strip()
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, company, role, location, status, application_date
            FROM applications
            WHERE company LIKE ? OR role LIKE ?
            ORDER BY application_date DESC
        """, (f"%{term}%", f"%{term}%")).fetchall()

    if not rows:
        print("No matching applications.")
        return

    for row in rows:
        print(" | ".join(str(value) for value in row))


def update_status():
    list_applications()
    application_id = input("Application ID: ").strip()
    if not application_id.isdigit():
        print("Invalid ID.")
        return

    new_status = choose_status()
    with connect() as conn:
        cursor = conn.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (new_status, int(application_id))
        )
    print("Status updated." if cursor.rowcount else "Application not found.")


def delete_application():
    list_applications()
    application_id = input("Application ID to delete: ").strip()
    if not application_id.isdigit():
        print("Invalid ID.")
        return

    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM applications WHERE id = ?",
            (int(application_id),)
        )
    print("Application deleted." if cursor.rowcount else "Application not found.")


def statistics():
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        rows = conn.execute("""
            SELECT status, COUNT(*)
            FROM applications
            GROUP BY status
            ORDER BY status
        """).fetchall()

    print(f"\nTotal applications: {total}")
    for status, count in rows:
        print(f"{status}: {count}")


def main():
    init_db()
    while True:
        print("""
========== JOB APPLICATION TRACKER ==========
1. Add application
2. List applications
3. Search applications
4. Update status
5. Delete application
6. View statistics
7. Exit
==============================================
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_application()
        elif choice == "2":
            list_applications()
        elif choice == "3":
            search_applications()
        elif choice == "4":
            update_status()
        elif choice == "5":
            delete_application()
        elif choice == "6":
            statistics()
        elif choice == "7":
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()

