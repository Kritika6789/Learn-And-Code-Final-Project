import sqlite3

def show_tables():
    conn = sqlite3.connect('prm.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("=== TABLES IN prm.db ===\n")
    for table in tables:
        table_name = table[0]
        print(f"--- Table: {table_name} ---")
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]
        print(" | ".join(columns))
        print("-" * 50)
        
        # Get data
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        
        if not rows:
            print("(empty)\n")
        else:
            for row in rows:
                print(" | ".join(str(r) for r in row))
            print("\n")
            
    conn.close()

if __name__ == "__main__":
    show_tables()
