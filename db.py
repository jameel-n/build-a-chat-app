import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.environ.get('DATABASE_PATH', ':memory:')

def get_db_connection():
    '''Get database connection (stub for testing)'''
    # In a real application, this would return a proper DB connection
    # For testing purposes, this is a placeholder
    return sqlite3.connect(DB_PATH)

@contextmanager
def db_transaction():
    '''Context manager for database transactions'''
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
