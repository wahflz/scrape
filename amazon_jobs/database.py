import atexit
import sqlite3
from os import path
from datetime import datetime, timedelta
from . import AMAZON_JOBS_DIR
from .structures import JobItem

SQLITE_DATABASE = path.join(AMAZON_JOBS_DIR, 'database.db')

def adapt_datetime(dt: datetime) -> str:
    return dt.isoformat()

def convert_datetime(ts: str) -> datetime:
    return datetime.fromisoformat(ts.decode('utf-8'))

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter('DATETIME', convert_datetime)

cnx = sqlite3.connect(SQLITE_DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
cur = cnx.cursor()
atexit.register(cnx.close)

def create_jobs_table():
    query = '''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_name TEXT NOT NULL,
            position_shifts INTEGER NOT NULL,
            position_code TEXT NOT NULL,
            location_city TEXT NOT NULL,
            location_state TEXT NOT NULL,
            location_distance REAL NOT NULL,
            timestamp DATETIME NOT NULL)
    '''

    cur.execute(query)
    cnx.commit()
    
def insert_job_item(item: JobItem):
    query = '''
        INSERT INTO jobs (
            position_name, 
            position_shifts, 
            position_code, 
            location_city, 
            location_state, 
            location_distance, 
            timestamp
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    cur.execute(query, (
        item.position.name, 
        item.position.shifts, 
        item.position.code, 
        item.location.city, 
        item.location.state, 
        item.location.distance, 
        datetime.now()
    ))
    cnx.commit()

def job_item_cached(item: JobItem, min_age: timedelta) -> bool:
    check_query = '''
        SELECT timestamp 
        FROM jobs 
        WHERE position_name = ? 
          AND position_code = ? 
          AND location_city = ? 
          AND location_state = ? 
          AND location_distance = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    '''
    cur.execute(check_query, (
        item.position.name, 
        item.position.code, 
        item.location.city, 
        item.location.state, 
        item.location.distance
    ))
    
    if res := cur.fetchone():
        return (datetime.now() - res[0]) <= min_age
    
    return False

create_jobs_table()
