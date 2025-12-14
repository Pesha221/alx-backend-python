import sqlite3


class DatabaseConnection:
    """Custom class-based context manager for database connections with parameterized query support."""

    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Open the database connection and return the cursor."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"✅ Connected to database: {self.db_name}")
        return self

    def execute_query(self, query, params=None):
        """
        Execute a SQL query safely using parameterized inputs.
        Example:
            db.execute_query("SELECT * FROM users WHERE age > ?", (25,))
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"⚠️ Database error: {e}")
            return []

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection safely with commit/rollback handling."""
        if exc_type:
            self.conn.rollback()
            print(f"❌ Error occurred: {exc_val}. Transaction rolled back.")
        else:
            self.conn.commit()
            print("💾 Transaction committed successfully.")
        self.conn.close()
        print(f"🔒 Connection to {self.db_name} closed.")


if __name__ == "__main__":
    # Example Usage
    with DatabaseConnection("users.db") as db:
        # Fetch all users
        users = db.execute_query("SELECT * FROM users")
        print("👥 All users:")
        for user in users:
            print(user)

        # Example of parameterized query
        older_users = db.execute_query("SELECT * FROM users WHERE age > ?", (25,))
        print("\n👵 Users older than 25:")
        for user in older_users:
            print(user)
