import sqlite3
import json  # Import json for storing lists

# Connect to the SQLite database
DATABASE_NAME = 'data/hh_aiest.db'  # Your SQLite database file

def insert_demo_data():
    try:
        db = sqlite3.connect(DATABASE_NAME)
        cur = db.cursor()

        # Create table if it doesn't exist
        cur.execute('''
        CREATE TABLE IF NOT EXISTS data_management_app_datajson (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            description TEXT,
            attachment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Insert demo data with attachment as a list of paths
        demo_data = [
            ("123", "Description for target 1", json.dumps(["https://uat16c.hunghingprinting.com/est_hd/for_ai_insert", "https://uat16c.hunghingprinting.com/web/login"])),
            ("23123", "Description for target 2", json.dumps(["path/to/file3"])),
            ("124124124", "Description for target 3", json.dumps(["path/to/file4", "path/to/file5", "path/to/file6"])),
        ]

        cur.executemany('''
        INSERT INTO data_management_app_datajson (target, description, attachment)
        VALUES (?, ?, ?)
        ''', demo_data)

        # Commit the changes
        db.commit()
        print("Demo data inserted successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        cur.close()
        db.close()

# Run the function to insert demo data
insert_demo_data()