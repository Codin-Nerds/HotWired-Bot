import asyncio

import asyncpg


async def main():
    """Create all the tables."""
    username = input(
        "Please enter the username of the PostgreSQL account: "
    )
    password = input(
        "Please enter the password of the PostgreSQL account: "
    )
    database = input(
        "Please enter the name of the database: "
    )
    con = await asyncpg.connect(
        host="127.0.0.1",
        user=username,
        password=password,
        database=database,
    )
    file = open("command.sql")
    statement = file.read()
    file.close()
    await con.execute(
        statement.format(owner=username)
    )

if __name__ == "__main__":
    asyncio.run(main())
