import sqlite3
from datetime import datetime
import os

db_path = 'instance/guest_faculty.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    if ('online_class',) in tables:
        print("\nChecking OnlineClass entries...")
        cursor.execute("SELECT id, subject, schedule_time, status, secure_token FROM online_class")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    else:
        print("\nOnlineClass table NOT FOUND!")
        
    conn.close()

print(f"\nCurrent Server Time (now): {datetime.now()}")
print(f"Current Server Time (utcnow): {datetime.utcnow()}") 
