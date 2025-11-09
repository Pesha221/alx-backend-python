import aiosqlite
import asyncio


class AsyncExecuteQuery:
    """Asynchronous context manager for executing SQL queries."""

    def __init__(self, db_name="users.db", query=None, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None
        self.results = None

    async def __aenter__(self):
        """Open async connection and execute query."""
        self.conn = await aiosqlite.connect(self.db_name)
        try:
            async with self.conn.execute(self.query, self.params or ()) as cursor:
                self.results = await cursor.fetchall()
        except Exception as e:
            print(f"⚠️ Database error: {e}")
            self.results = []
        return self.results

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback depending on errors and close connection."""
        if exc_type:
            await self.conn.rollback()
            print(f"❌ Error occurred: {exc_val}. Rolled back transaction.")
        else:
            await self.conn.commit()
        await self.conn.close()
        print("🔒 Async database connection closed.")


async def main():
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)

    async with AsyncExecuteQuery("users.db", query, params) as results:
        print("👵 Users older than 25:")
        for user in results:
            print(user)


if __name__ == "__main__":
    asyncio.run(main())
