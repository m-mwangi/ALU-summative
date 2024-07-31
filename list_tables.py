import sqlite3
import os

database_path = 'instance/site.db'

if not os.path.exists(database_path):
    print(f"Error: The database file {database_path} does not exist.")
else:
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Retrieve table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tables in database:")
        for table in tables:
            print(table[0])
        
        conn.close()
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")