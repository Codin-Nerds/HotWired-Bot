from discord.ext.commands import Cog, Context, command
from discord import Embed
from bot.core.bot import Bot
from bot import config

from uuid import uuid4
import datetime
import asyncio
import random
import sqlite3


class Reminders(Cog):
    """Provide in-channel reminder functionality."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.db_connection = self.create_db_connection(config.db_location)
        self.create_reminders_table()
        self.bot.loop.create_task(self.reschedule_reminders())

    @command(aliases=["setreminder", "remindme"])
    async def remind(self, ctx: Context, time: str, *reason) -> None:
        """Sets a reminder to ping the user after a given period of time."""

        if not time[:-1].isdigit() or time[-1:] not in "smhd":
            embed = Embed(
                title=random.choice(config.NEGATIVE_REPLIES),
                description="Please double-check your input arguments and try again.",
            )
            await ctx.send(embed=embed)
        else:
            expiration = datetime.timedelta(0, self.time_in_seconds(time)) + datetime.datetime.now()
            reason = " ".join(reason)
            reminder = {
                "id": str(uuid4()),
                "user": ctx.message.author.id,
                "reason": reason,
                "channel": ctx.channel.id,
                "expiration": expiration.isoformat(),
                "jump_url": ctx.message.jump_url,
            }

            self.save_reminder(reminder)
            await self.send_reminder_scheduled_confirmation(
                reminder, self.time_in_seconds(time)
            )
            await self.schedule_reminder(
                reminder, time_until_expiration=self.time_in_seconds(time)
            )

    async def schedule_reminder(
        self, reminder: dict, time_until_expiration=None
    ) -> None:
        """Schedule reminder"""
        if not self.ensure_reminder_valid(reminder):
            self.delete_reminder(reminder['id'])
            return

        if time_until_expiration is None:
            expiration = datetime.datetime.fromisoformat(
                reminder["expiration"]
            ).timestamp()
            time_until_expiration = expiration - datetime.datetime.now().timestamp()

        # The use of -1 instead of 0 is to account for latency and processing time
        if time_until_expiration > -1:

            if time_until_expiration < 0:
                time_until_expiration = 0

            await asyncio.sleep(time_until_expiration)
            await self.send_reminder(reminder)
            self.delete_reminder(reminder["id"])

        elif time_until_expiration < -1:
            await self.send_reminder(reminder, late=True)
            self.delete_reminder(reminder["id"])

    async def send_reminder_scheduled_confirmation(
        self, reminder: dict, time_until_expiration: int
    ) -> None:
        """Send embed confirming reminder created successfully"""
        embed = Embed(
            title=f"⏰ {random.choice(config.POSITIVE_REPLIES)}",
            description=f"You will be reminded in {self.humanize_time(time_until_expiration)}",
        )
        channel = self.bot.get_channel(reminder["channel"])
        await channel.send(
            f"<@{reminder['user']}> You have set a reminder!", embed=embed
        )

    async def send_reminder(self, reminder: dict, late=False) -> None:
        """Send the reminder"""
        embed = Embed(
            title="Your reminder has arrived!", description=f"`{reminder['reason']}`",
        )

        if late:
            embed.title = "It's a bit late :("
            embed.description += f"\nYour reminder was late by {self.time_until_date(reminder['expiration'])}"

        embed.description += (
            f"\n[Jump to when you created this reminder.]({reminder['jump_url']})"
        )
        channel = self.bot.get_channel(reminder["channel"])
        await channel.send(f"<@{reminder['user']}>", embed=embed)

    def ensure_reminder_valid(self, reminder: dict) -> bool:
        """Ensure that both the user and the channel exist"""
        user = self.bot.get_user(reminder['user'])
        channel = self.bot.get_channel(reminder['channel'])

        if not channel or not user:
            return False

        return True

    def save_reminder(self, reminder: dict) -> None:
        """Save reminder in database"""
        columns = ", ".join(reminder.keys())
        values = ", ".join("?" * len(reminder.keys()))
        query = f"INSERT INTO reminders ({columns}) VALUES ({values})"

        cursor = self.db_connection.cursor()
        cursor.execute(query, list(reminder.values()))
        self.db_connection.commit()

    def get_reminders(self) -> list:
        """Retrieve all reminders in database"""
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT * FROM reminders")
            result = cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Failed to fetch reminders from database : {e}")

    async def reschedule_reminders(self):
        """Get reminders from database and reschedule"""
        reminders_in_db = self.get_reminders()

        columns = ("id", "user", "reason", "channel", "expiration", "jump_url")
        for reminder in reminders_in_db:
            reminder = dict(zip(columns, reminder))
            await self.schedule_reminder(reminder)

    def create_reminders_table(self):
        """Create reminders table in database if it does not exist"""
        create_reminders_table_query = """
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            user INTEGER NOT NULL,
            reason TEXT NOT NULL,
            channel INTEGER NOT NULL,
            expiration TEXT NOT NULL,
            jump_url TEXT NOT NULL
        );
        """

        cursor = self.db_connection.cursor()
        cursor.execute(create_reminders_table_query)
        self.db_connection.commit()

    def delete_reminder(self, reminder_id: str) -> None:
        """Delete reminder from database"""
        cursor = self.db_connection.cursor()
        cursor.execute(f'DELETE FROM reminders WHERE ID="{reminder_id}"')
        self.db_connection.commit()

    @staticmethod
    def create_db_connection(path):
        """Create connection to database"""
        connection = None
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(f"Error ocurred while trying to create database connection : {e}")

        return connection

    def time_until_date(self, datetime_in_isoformat: str) -> str:
        """Returns time until a given date (isoformat string) is reached (in the form : 0 days, 00h 00m 00s)"""
        expiration = datetime.datetime.fromisoformat(datetime_in_isoformat).timestamp()
        time_until_date = expiration - datetime.datetime.now().timestamp()

        if time_until_date < 0:
            time_until_date = 0 - time_until_date
        return self.humanize_time(time_until_date)

    @staticmethod
    def humanize_time(time_in_seconds: int) -> str:
        """converts time in seconds to a more readable format (0 days 00h 00m 00s)"""
        timedelta = str(datetime.timedelta(seconds=time_in_seconds))
        hours, minutes, seconds = timedelta.split(":")
        return f"{hours}h {minutes}m {seconds}s"

    @staticmethod
    def time_in_seconds(time: str) -> int:
        """converts time input from user (e.g 23h, 5m, 300s) to time in seconds"""
        time_unit = time[-1:]
        time_unit_factors = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
        }

        if time_unit.isdigit():
            return int(time)
        return int(time[:-1]) * time_unit_factors[time_unit]


def setup(bot):
    bot.add_cog(Reminders(bot))
