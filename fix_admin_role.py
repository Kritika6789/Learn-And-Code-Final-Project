import sqlite3
conn = sqlite3.connect('prm.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET role='ADMIN' WHERE username='admin'")
conn.commit()
conn.close()
print("Updated admin role to ADMIN")
