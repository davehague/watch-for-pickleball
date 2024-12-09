import sqlite3
import logging


class PersistentData:
    def __init__(self, db_name='events.db'):
        self.db_name = db_name
        self.conn = None
        self.initialize_db()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def initialize_db(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS facilities (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    username TEXT,
                    password TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    date TEXT,
                    time TEXT,
                    facilityId INTEGER,
                    FOREIGN KEY (facilityId) REFERENCES facilities(id),
                    UNIQUE(title, date, time, facilityId)
                )
            ''')
            self.conn.commit()
            logging.info("Database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Error initializing database: {e}")
            raise

    def get_stored_events(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT title, date, time, facilityId FROM events')
            stored_events = cursor.fetchall()
            stored_event_details = {(event[0], event[1], event[2], event[3]) for event in stored_events}
            return stored_events, stored_event_details
        except sqlite3.Error as e:
            logging.error(f"Error retrieving stored events: {e}")
            raise

    def get_facilities(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, name, url, platform, username, password, schedule FROM facilities')
            facilities = cursor.fetchall()
            return facilities
        except sqlite3.Error as e:
            logging.error(f"Error retrieving facilities: {e}")
            raise

    def insert_events(self, events):
        try:
            cursor = self.conn.cursor()
            for event in events:
                cursor.execute('''
                    INSERT OR IGNORE INTO events (title, date, time, facilityId) VALUES (?, ?, ?, ?)
                ''', (event['title'], event['date'], event['time'], event['facilityId']))
            self.conn.commit()
            logging.info(f"Inserted {len(events)} new events")
        except sqlite3.Error as e:
            logging.error(f"Error inserting events: {e}")
            raise

    def insert_facility(self, name, url, platform, username=None, password=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO facilities (name, url, platform, username, password) VALUES (?, ?, ?, ?, ?)
            ''', (name, url, platform, username, password))
            self.conn.commit()
            logging.info(f"Inserted new facility: {name}")
        except sqlite3.Error as e:
            logging.error(f"Error inserting facility: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")
