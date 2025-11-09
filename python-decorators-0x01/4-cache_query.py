import time
import sqlite3
import functools
from datetime import datetime


query_cache = {}
CACHE_TTL = 300  # cache expiry time in seconds (5 minutes)


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


def cache_query(func):
    """
    Decorator to cache query results based on SQL query string with TTL expiration.
    Avoids redundant database calls within the cache duration.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get("query")
        current_time = time.time()

        # If cached and still valid
        if query in query_cache:
            cached_time, result = query_cache[query]
            if current_time - cached_time < CACHE_TTL:
                print(f"[{datetime.now()}] Cache hit for query: {query}")
                return result
            else:
                print(f"[{datetime.now()}] Cache expired for query: {query}. Refreshing cache...")

        # Otherwise, execute the function and store in cache
        print(f"[{datetime.now()}] Cache miss for query: {query}. Fetching from DB...")
        result = func(*args, **kwargs)
        query_cache[query] = (current_time, result)
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users with caching to avoid redundant DB hits"""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


if __name__ == "__main__":
    # First call — DB hit
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("First call result:", users[:3])

    # Second call — cached (within TTL)
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("Second call result:", users_again[:3])

    # Simulate cache expiration
    print("\nSimulating cache expiration...")
    time.sleep(CACHE_TTL + 1)

    # Third call — cache expired, refetch from DB
    users_third = fetch_users_with_cache(query="SELECT * FROM users")
    print("Third call after TTL result:", users_third[:3])
