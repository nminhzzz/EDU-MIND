import sqlite3
import os

db_path = r"d:\AI Learning Assistant Platform\Backend\scratch\test_db.sqlite"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    for row in cur.fetchall():
        print(row[0])
    conn.close()
else:
    print("Database file does not exist!")
