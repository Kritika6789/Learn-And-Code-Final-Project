import sqlite3

def migrate():
    conn = sqlite3.connect('prm.db')
    cursor = conn.cursor()
    
    print("Starting data migration...")
    # Update users table with department and designation from resource
    cursor.execute("""
        UPDATE users 
        SET department = (SELECT department FROM resource WHERE resource.user_id = users.id),
            designation = (SELECT designation FROM resource WHERE resource.user_id = users.id)
        WHERE EXISTS (SELECT 1 FROM resource WHERE resource.user_id = users.id)
    """)
    print(f"Updated {cursor.rowcount} users with department and designation.")
    
    # Drop columns from resource table
    print("Dropping columns from resource table...")
    try:
        cursor.execute("ALTER TABLE resource DROP COLUMN full_name")
        cursor.execute("ALTER TABLE resource DROP COLUMN email")
        cursor.execute("ALTER TABLE resource DROP COLUMN department")
        cursor.execute("ALTER TABLE resource DROP COLUMN designation")
        print("Columns dropped successfully.")
    except Exception as e:
        print(f"Error dropping columns: {e}")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
