import sqlite3

def setup_db():
    # Inventory Database
    conn_inv = sqlite3.connect("inventory.db")
    cursor_inv = conn_inv.cursor()
    cursor_inv.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            assigned_to TEXT DEFAULT 'Slobodno'
        )
    ''')
    conn_inv.commit()
    conn_inv.close()

    # Employees Database
    conn_emp = sqlite3.connect("employees.db")
    cursor_emp = conn_emp.cursor()
    cursor_emp.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company TEXT NOT NULL
        )
    ''')
    conn_emp.commit()
    conn_emp.close()

setup_db()
print("Database and tables recreated successfully!")