import sqlite3
import functools
from datetime import datetime


def with_db_connection(func):
    """Decorator to handle opening and closing the database connection automatically"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def log_transaction(message):
    """Helper function to log transaction activity with timestamps"""
    with open("transactions.log", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")


def transactional(func):
    """Decorator to manage database transactions automatically"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            log_transaction(f"COMMIT: {func.__name__} executed successfully")
        except Exception as e:
            conn.rollback()
            log_transaction(f"ROLLBACK: {func.__name__} failed with error: {e}")
            print(f"Transaction rolled back due to error: {e}")
            raise
        return result
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    """Update a user's email address safely within a transaction"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


# Example usage (only runs when executed directly)
if __name__ == "__main__":
    update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
    print("User email updated successfully.")
