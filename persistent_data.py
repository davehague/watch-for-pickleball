import sqlite3


class PersistentData:
    def __init__(self, db_name='events.db'):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.initialize_db()

    def initialize_db(self):
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

    def get_stored_events(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT title, date, time, facilityId FROM events')
        stored_events = cursor.fetchall()
        stored_event_details = {(event[0], event[1], event[2], event[3]) for event in stored_events}
        return stored_events, stored_event_details

    def get_facilities(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, url, platform, username, password FROM facilities')
        facilities = cursor.fetchall()
        return facilities

    def insert_events(self, events):
        cursor = self.conn.cursor()
        for event in events:
            cursor.execute('''
                INSERT OR IGNORE INTO events (title, date, time, facilityId) VALUES (?, ?, ?, ?)
            ''', (event['title'], event['date'], event['time'], event['facilityId']))
        self.conn.commit()

    def insert_facility(self, name, url, platform, username=None, password=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO facilities (name, url, platform, username, password) VALUES (?, ?, ?, ?, ?)
        ''', (name, url, platform, username, password))
        self.conn.commit()

    def close(self):
        self.conn.close()
