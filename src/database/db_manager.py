import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="travelai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
    
    def save_trip(self, destination, start_date, end_date, budget, interests, itinerary):
        """Save a trip to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trips (destination, start_date, end_date, budget, interests, itinerary_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (destination, start_date, end_date, budget, json.dumps(interests), json.dumps(itinerary)))
        trip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return trip_id
    
    def get_all_trips(self):
        """Retrieve all trips"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trips ORDER BY created_at DESC")
        trips = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return trips
    
    def save_agent_finding(self, trip_id, agent_name, findings):
        """Save agent findings for debugging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_findings (trip_id, agent_name, findings)
            VALUES (?, ?, ?)
        """, (trip_id, agent_name, json.dumps(findings)))
        conn.commit()
        conn.close()