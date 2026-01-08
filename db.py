import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Optional, Any

DB_PATH = os.environ.get('DATABASE_PATH', ':memory:')
CONNECTION_TIMEOUT = 30
MAX_RETRIES = 3

def get_db_connection(timeout: Optional[int] = None) -> sqlite3.Connection:
    '''Get database connection (stub for testing)'''
    # In a real application, this would return a proper DB connection
    # For testing purposes, this is a placeholder
    effective_timeout = timeout or CONNECTION_TIMEOUT
    logging.debug(f"Connecting to database: {DB_PATH}")
    return sqlite3.connect(DB_PATH, timeout=effective_timeout)

@contextmanager
def db_transaction(timeout: Optional[int] = None):
    '''Context manager for database transactions'''
    conn = get_db_connection(timeout)
    try:
        yield conn
        conn.commit()
        logging.debug("Transaction committed successfully")
    except Exception as e:
        conn.rollback()
        logging.error(f"Transaction rolled back due to: {e}")
        raise e
    finally:
        conn.close()

def execute_query(query: str, params: tuple = (), fetch: bool = True) -> Any:
    '''Execute a query and optionally fetch results'''
    with db_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        return cursor.rowcount

def table_exists(table_name: str) -> bool:
    '''Check if a table exists in the database'''
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    results = execute_query(query, (table_name,))
    return len(results) > 0
