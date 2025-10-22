import sqlite3

def get_db_connection():
    '''Get database connection (stub for testing)'''
    # In a real application, this would return a proper DB connection
    # For testing purposes, this is a placeholder
    return sqlite3.connect(':memory:')
