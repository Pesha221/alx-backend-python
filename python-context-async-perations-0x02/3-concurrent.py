import aiosqlite
import asyncio

DB_NAME = "users.db"


async def fetch_query(conn, query, params=None):
    """
    Execute a single query asynchronously and return results.
    """
    async with conn.execute(query, params or ()) as cursor:
        results = await cursor.fetchall()
        return results


async def fetch_concurrently(queries):
    """
    Run multiple queries concurrently.
    queries: list of tuples -> (query_string, params)
    """
    async with aiosqlite.connect(DB_NAME) as conn:
        tasks = [fetch_query(conn, q, p) for q, p in queries]
        results_list = await asyncio.gather(*tasks)

        # Print results for each query
        for i, (query, _) in enumerate(queries):
            print(f"\n📝 Results for query {i+1}: {query}")
            for row in results_list[i]:
                print(row)

        return results_list


if __name__ == "__main__":
    # Example: list of queries with optional parameters
    queries_to_run = [
        ("SELECT * FROM users", None),
        ("SELECT * FROM users WHERE age > ?", (40,)),
        ("SELECT * FROM users WHERE age < ?", (30,))
    ]

    asyncio.run(fetch_concurrently(queries_to_run))
