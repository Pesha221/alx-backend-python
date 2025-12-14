import aiosqlite
import asyncio

DB_NAME = "users.db"


async def fetch_query(query, params=None):
    """Reusable async function to execute a query and fetch results."""
    async with aiosqlite.connect(DB_NAME) as conn:
        async with conn.execute(query, params or ()) as cursor:
            results = await cursor.fetchall()
            return results


async def async_fetch_users():
    """Fetch all users asynchronously."""
    results = await fetch_query("SELECT * FROM users")
    print("👥 All users:")
    for row in results:
        print(row)
    return results


async def async_fetch_older_users():
    """Fetch users older than 40 asynchronously."""
    results = await fetch_query("SELECT * FROM users WHERE age > ?", (40,))
    print("\n👴 Users older than 40:")
    for row in results:
        print(row)
    return results


async def fetch_concurrently():
    """Run both queries concurrently using asyncio.gather."""
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
