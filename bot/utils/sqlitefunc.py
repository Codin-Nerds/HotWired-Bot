import aiosqlite


# Initialize the connection.
database_path = "bot/assets/antispam.db"

async with aiosqlite.connect(database_path) as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS antispam (
        serverid integer PRIMARY KEY,
        banlock integer NOT NULL,
        kicklock integer NOT NULL,
        serverlock integer NOT NULL,
        invitelock integer NOT NULL,
        linklock integer NOT NULL,
        maintenancemode integer NOT NULL
    )
    """)
    db.commit()


def enable_banlock(serverid: int) -> None:
    query = "SELECT banlock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            banlock = await cursor.fetchone()
            banlock = banlock[0]

        if not banlock:
            sql = "INSERT INTO antispam(banlock) values(1)"
            db.execute(sql)
            db.commit()


def disable_banlock(serverid: int) -> None:
    query = "SELECT banlock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            banlock = await cursor.fetchone()
            banlock = banlock[0]

        if banlock:
            sql = "INSERT INTO antispam(banlock) values(0)"
            db.execute(sql)
            db.commit()


def enable_kicklock(serverid: int) -> None:
    query = "SELECT kicklock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            kicklock = await cursor.fetchone()
            kicklock = kicklock[0]

        if not kicklock:
            sql = "INSERT INTO antispam(kicklock) values(1)"
            db.execute(sql)
            db.commit()


def disable_kicklock(serverid: int) -> None:
    query = "SELECT kicklock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            kicklock = await cursor.fetchone()
            kicklock = kicklock[0]

        if kicklock:
            sql = "INSERT INTO antispam(kicklock) values(0)"
            db.execute(sql)
            db.commit()


def enable_serverlock(serverid: int) -> None:
    query = "SELECT serverlock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            serverlock = await cursor.fetchone()
            serverlock = serverlock[0]

        if not serverlock:
            sql = "INSERT INTO antispam(serverlock) values(1)"
            db.execute(sql)
            db.commit()


def disable_serverlock(serverid: int) -> None:
    query = "SELECT serverlock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            serverlock = await cursor.fetchone()
            serverlock = serverlock[0]

        if serverlock:
            sql = "INSERT INTO antispam(serverlock) values(0)"
            db.execute(sql)
            db.commit()


def enable_invitelock(serverid: int) -> None:
    query = "SELECT invitelock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            invitelock = await cursor.fetchone()
            invitelock = invitelock[0]

        if not invitelock:
            sql = "INSERT INTO antispam(invitelock) values(1)"
            db.execute(sql)
            db.commit()


def disable_invitelock(serverid: int) -> None:
    query = "SELECT invitelock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            invitelock = await cursor.fetchone()
            invitelock = invitelock[0]

        if invitelock:
            sql = "INSERT INTO antispam(invitelock) values(0)"
            db.execute(sql)
            db.commit()


def enable_linklock(serverid: int) -> None:
    query = "SELECT linklock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            linklock = await cursor.fetchone()
            linklock = linklock[0]

        if not linklock:
            sql = "INSERT INTO antispam(linklock) values(1)"
            db.execute(sql)
            db.commit()


def disable_linklock(serverid: int) -> None:
    query = "SELECT linklock FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            linklock = await cursor.fetchone()
            linklock = linklock[0]

        if linklock:
            sql = "INSERT INTO antispam(linklock) values(0)"
            db.execute(sql)
            db.commit()


def enable_maintenancemode(serverid: int) -> None:
    query = "SELECT maintenancemode FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            maintenancemode = await cursor.fetchone()
            maintenancemode = maintenancemode[0]

        if not maintenancemode:
            sql = "INSERT INTO antispam(maintenancemode) values(1)"
            db.execute(sql)
            db.commit()


def disable_maintenancemode(serverid: int) -> None:
    query = "SELECT maintenancemode FROM antispam WHERE serverid = ?"

    async with aiosqlite.connect(database_path) as db:
        async with db.execute(query, (serverid)) as cursor:
            maintenancemode = await cursor.fetchone()
            maintenancemode = maintenancemode[0]

        if maintenancemode:
            sql = "INSERT INTO antispam(maintenancemode) values(0)"
            db.execute(sql)
            db.commit()
