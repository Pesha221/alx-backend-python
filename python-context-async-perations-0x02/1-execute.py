import sqlite3

class ExecuteQuery:
    """Reusable context manager to execute a database query safely."""

    def __init__(self, db_name="users.db", query=None, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """Open database connection and execute the provided query."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        try:
            if self.params:
                self.cursor.execute(self.query, self.params)
            else:
                self.cursor.execute(self.query)
            self.results = self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"⚠️ Database error: {e}")
            self.results = []
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit changes if no exception, rollback otherwise, and close connection."""
        if exc_type:
            self.conn.rollback()
            print(f"❌ Error occurred: {exc_val}. Rolled back transaction.")
        else:
            self.conn.commit()
        self.conn.close()
        print("🔒 Database connection closed.")


if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db", query, params) as results:
        print("👵 Users older than 25:")
        for user in results:
            print(user)
