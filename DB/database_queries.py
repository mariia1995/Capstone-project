import sqlite3


class DBBase:
    def __init__(self):
        self.db_name = 'database.db'
        self.conn = None

    def connect(self):
        """ Connect to db """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)
        return self.conn


    def execute_query(self, query, params=None):
        """Execute SQL-query."""
        try:
            cursor = self.conn.cursor()
        except Exception:
            self.conn = self.connect()
            cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            self.conn.rollback()
            raise

    def close(self):

        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Open automatically."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close automatically."""
        self.close()
