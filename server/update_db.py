import sqlite3
import sys

def update_email():
    try:
        conn = sqlite3.connect('prm.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = 'admin@techserve.com' WHERE username = 'admin'")
        conn.commit()
        print("Updated admin email.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

def update_schema():
    try:
        conn = sqlite3.connect('prm.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE resource ADD COLUMN timesheet_frozen BOOLEAN DEFAULT 0")
        conn.commit()
        print("Added timesheet_frozen column to resource table.")
    except Exception as e:
        if "duplicate column name" in str(e):
            print("Column timesheet_frozen already exists.")
        else:
            print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_email()
    update_schema()
