import time
import sqlite3
import functools
from datetime import datetime


def log_message(message):
    """Helper to log messages to retry.log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("retry.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def with_db_connection(func):
    """Decorator to automatically handle database connection opening and closing"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a database function if it raises an exception.
    Retries up to 'retries' times with 'delay' seconds between attempts.
    Logs all retry attempts and failures to retry.log.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    attempt += 1
                    msg = f"Transient error: {e}. Retry {attempt}/{retries}..."
                    print(msg)
                    log_message(msg)
                    time.sleep(delay)
                except Exception as e:
                    msg = f"Fatal error: {e}. Aborting retries."
                    print(msg)
                    log_message(msg)
                    raise
            msg = f"Operation failed after {retries} retries."
            print(msg)
            log_message(msg)
            raise Exception(msg)
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch all users with automatic retry on transient database errors"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print(users)
    except Exception as e:
        log_message(f"Final failure: {e}")
        print(f"Final failure: {e}")
