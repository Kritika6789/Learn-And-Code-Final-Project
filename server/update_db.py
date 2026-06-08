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

if __name__ == '__main__':
    update_email()
