import sqlite3

conn = sqlite3.connect('prm.db')
cur = conn.cursor()
cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'trigger')")
for row in cur.fetchall():
    if row[0]:
        print(row[0])
conn.close()
