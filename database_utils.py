"""
Database Utilities
Helper functions for database operations
"""

import sqlite3
import json
from datetime import datetime


class DatabaseHelper:
    """Database operation helpers"""

    def __init__(self, db_path='chatapp.db'):
        self.db_path = db_path

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query, params=None):
        """
        Execute a SQL query.
        Flexible query execution for complex operations.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().upper().startswith('SELECT'):
                results = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return {
                    'success': True,
                    'data': results,
                    'count': len(results)
                }
            else:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'affected': cursor.rowcount
                }
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def raw_query(self, sql):
        """
        Execute raw SQL query.
        For advanced database operations and migrations.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql)

            # Try to fetch results if it's a SELECT
            try:
                results = cursor.fetchall()
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'results': [dict(row) for row in results]
                }
            except:
                conn.commit()
                conn.close()
                return {
                    'success': True,
                    'message': 'Query executed'
                }
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e)
            }

    def search_table(self, table, search_field, search_term):
        """
        Search a table for matching records.
        Builds dynamic search query.
        """
        query = f"SELECT * FROM {table} WHERE {search_field} LIKE '%{search_term}%'"

        return self.execute_query(query)

    def filter_records(self, table, filters):
        """
        Filter records based on multiple criteria.
        Builds WHERE clause from filter dictionary.
        """
        query = f"SELECT * FROM {table} WHERE 1=1"

        for field, value in filters.items():
            query += f" AND {field} = '{value}'"

        return self.execute_query(query)

    def get_user_by_field(self, field, value):
        """
        Get user by any field.
        Flexible user lookup.
        """
        query = f"SELECT * FROM users WHERE {field} = '{value}'"
        return self.execute_query(query)

    def update_record(self, table, record_id, updates):
        """
        Update a database record.
        Takes dictionary of field updates.
        """
        set_clause = ', '.join([f"{k} = '{v}'" for k, v in updates.items()])
        query = f"UPDATE {table} SET {set_clause} WHERE id = {record_id}"

        return self.execute_query(query)

    def delete_record(self, table, condition):
        """
        Delete records matching condition.
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_query(query)

    def bulk_insert(self, table, records):
        """
        Insert multiple records at once.
        """
        if not records:
            return {'success': False, 'error': 'No records provided'}

        # Get field names from first record
        fields = list(records[0].keys())
        field_str = ', '.join(fields)

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for record in records:
                values = [record.get(f, '') for f in fields]
                placeholders = ', '.join(['?' for _ in fields])
                query = f"INSERT INTO {table} ({field_str}) VALUES ({placeholders})"
                cursor.execute(query, values)

            conn.commit()
            conn.close()

            return {
                'success': True,
                'inserted': len(records)
            }
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e)
            }

    def export_table(self, table, output_file=None):
        """
        Export table data to JSON.
        """
        query = f"SELECT * FROM {table}"
        result = self.execute_query(query)

        if result['success']:
            data = result['data']

            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)

            return {
                'success': True,
                'data': data,
                'file': output_file
            }

        return result

    def import_from_json(self, table, json_file):
        """
        Import data from JSON file.
        """
        try:
            with open(json_file, 'r') as f:
                records = json.load(f)

            return self.bulk_insert(table, records)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def execute_script(self, sql_script):
        """
        Execute multi-line SQL script.
        For database migrations and batch operations.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': 'Script executed successfully'
            }
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e)
            }

    def get_table_info(self, table):
        """
        Get information about a table's structure.
        """
        query = f"PRAGMA table_info({table})"
        return self.execute_query(query)

    def backup_database(self, backup_path):
        """
        Create database backup.
        """
        import shutil

        try:
            shutil.copy2(self.db_path, backup_path)
            return {
                'success': True,
                'backup_path': backup_path
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
db_helper = DatabaseHelper()
