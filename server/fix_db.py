import sqlite3
import sys
import os

def fix_db():
    db_path = 'prm.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if 'role' column exists in 'users'
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'role' not in columns:
            print("Adding 'role' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'EMPLOYEE'")
            conn.commit()
            print("Successfully added 'role' column.")
        else:
            print("'role' column already exists in 'users'.")
            
        # Also drop employees if it exists, so resource can be used instead, 
        # or we could just rename the table.
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
        if cursor.fetchone():
            print("Renaming 'employees' table to 'resource'...")
            cursor.execute("ALTER TABLE employees RENAME TO resource")
            conn.commit()
            print("Successfully renamed 'employees' to 'resource'.")
        
    except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    fix_db()
