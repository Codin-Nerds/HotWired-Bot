import asyncio
import datetime
import itertools
import contextlib
import json

from discord import Color, Embed, Channel, Forbidden, HTTPException, Role, utils
from discord.ext.commands import Cog, Context, group, has_permissions

from bot.core import Bot


BDAY_JSON_PATH = "assets/bday.json"

JSON_CONFIG = {
    "roles": {},
    "channels": {},
    "birthdays": {},
    "yesterday": []
}

ROLE_SET = ":white_check_mark: The birthday role on **{s}** has been set to: **{r}**."
BDAY_INVALID = ":x: The birthday date you entered is invalid. It must be `MM-DD`."
BDAY_SET = ":white_check_mark: Your birthday has been set to: **{}**."
CHANNEL_SET = ":white_check_mark: The channel for announcing birthdays on **{s}** has been set to: **{c}**."
BDAY_REMOVED = ":put_litter_in_its_place: Your birthday has been removed."


class Birthday(Cog):
    """Announces birthdays and gives them a special role for the whole day."""
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.load_data()
        self.bday_loop = asyncio.ensure_future(self.initialise())

    async def initialise(self) -> None:
        await self.bot.wait_until_ready()

        with contextlib.suppress(RuntimeError):
            while self == self.bot.get_cog(self.__class__.__name__):

                now = datetime.datetime.utcnow()
                tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

                await asyncio.sleep((tomorrow - now).total_seconds())

                self.clean_yesterday_bdays()
                self.do_today_bdays()
                self.save_data()

    def __unload(self) -> None:
        self.bday_loop.cancel()

    @group(pass_context=True)
    async def bday(self, ctx: Context) -> None:
        """birthday setup."""
        pass

    @bday.command(no_pm=True)
    @has_permissions(manage_roles=True)
    async def channel(self, ctx: Context, channel: Channel) -> None:
        """Sets the birthday announcement channel for this server."""
        self.config["channels"][ctx.guild.id] = channel.id
        self.save_data()
        await ctx.send(CHANNEL_SET.format(s=ctx.guild.name, c=channel.name))

    @bday.command()
    @has_permissions(manage_roles=True)
    async def role(self, ctx: Context, role: Role) -> None:
        """Sets the birthday role for this server."""
        self.config["roles"][ctx.guild.id] = role.id
        self.save_data()
        await ctx.send(ROLE_SET.format(s=ctx.guild.name, r=role.name))

    @bday.command(aliases=["del", "clear"])
    async def remove(self, ctx: Context) -> None:
        """Unsets your birthday date."""
        self.remove_user_bday(ctx.author.id)
        self.save_data()
        await ctx.send(self.BDAY_REMOVED)

    @bday.command()
    async def set(self, ctx: Context, date: str, year: int = None) -> None:
        """
        Sets your birthday date
        The given date must be given as: MM-DD
        Year is optional. If ungiven, the age won't be displayed.
        """
        birthday = self.parse_date(date)

        if birthday is None:
            await ctx.send(BDAY_INVALID)

        else:
            self.remove_user_bday(ctx.author.id)
            self.config["birthdays"].setdefault(str(birthday.toordinal()), {})[ctx.author.id] = year
            self.save_data()

            bday_month_str = birthday.strftime("%B")
            bday_day_str = birthday.strftime("%d").lstrip("0")

            await self.bot.send_message(BDAY_SET.format(f"{bday_month_str} {bday_day_str}"))

    @bday.command()
    async def list(self, ctx: Context) -> None:
        """
        Lists all the birthdays
        If a user has their year set, it will display the age they'll get after their birthday this year.
        """
        self.clean_bdays()
        self.save_data()

        bdays = self.config["birthdays"]
        this_year = datetime.date.today().year

        embed = Embed(title="Birthday List", color=Color.blue())

        for k, g in itertools.groupby(
            sorted(datetime.datetime.fromordinal(int(o)) for o in bdays.keys()),
                lambda i: i.month):

            value = "\n".join(date.strftime("%d").lstrip("0") + ": " + ", ".join(f"<@!{u_id}>" + (""
                                                                                                  if year is None else f" ({this_year - int(year)})")
                                                                                 for u_id, year in bdays.get(str(date.toordinal()), {}).items())
                              for date in g if len(bdays.get(str(date.toordinal()))) > 0)

            if not value.isspace():
                embed.add_field(name=datetime.datetime(year=1, month=k, day=1).strftime("%B"), value=value)

        await ctx.send(embed=embed)

    async def clean_bday(self, user_id: int) -> None:
        for server_id, role_id in self.config["roles"].items():
            server = self.bot.get_server(server_id)

            if server is not None:
                role = utils.find(lambda role: role.id == role_id, server.roles)
                member = server.get_member(user_id)

                if member is not None and role is not None and role in member.roles:
                    await self.bot.remove_roles(member, role)

    async def handle_bday(self, user_id: int, year: int) -> None:
        embed = Embed(color=Color.gold())

        if year is not None:
            age = datetime.date.today().year - int(year)
            embed.description = f"<@!{user_id}> is now **{age} years old**. :tada: "
        else:
            embed.description = f"It's <@!{user_id}>'s birthday today! :tada: "

        for server_id, channel_id in self.config["channels"].items():
            server = self.bot.get_server(server_id)

            if server is not None:
                member = server.get_member(user_id)

                if member is not None:
                    role_id = self.config["roles"].get(server_id)

                    if role_id is not None:
                        role = utils.find(lambda r: r.id == role_id, server.roles)

                        if role is not None:
                            try:
                                await self.bot.add_roles(member, role)
                            except (Forbidden, HTTPException):
                                pass
                            else:
                                self.config["yesterday"].append(member.id)

                    channel = server.get_channel(channel_id)

                    if channel is not None:
                        await channel.send(embed=embed)

    def clean_bdays(self) -> None:
        """
        Cleans the birthday entries with no user's birthday
        Also removes birthdays of users who aren't in any visible server anymore
        Happens when someone changes their birthday and there's nobody else in the same day.
        """
        birthdays = self.config["birthdays"]

        for date, bdays in birthdays.copy().items():
            for user_id, _year in bdays.copy().items():

                if not any(s.get_member(user_id) is not None for s in self.bot.servers):
                    del birthdays[date][user_id]

            if len(bdays) == 0:
                del birthdays[date]

    def remove_user_bday(self, user_id: int) -> None:
        for date, user_ids in self.config["birthdays"].items():
            if user_id in user_ids:
                del self.config["birthdays"][date][user_id]

    def clean_yesterday_bdays(self) -> None:
        for user_id in self.config["yesterday"]:
            asyncio.ensure_future(self.clean_bday(user_id))

        self.config["yesterday"].clear()

    def do_today_bdays(self) -> None:
        this_date = datetime.datetime.utcnow().date().replace(year=1)

        for user_id, year in self.config["birthdays"].get(str(this_date.toordinal()), {}).items():
            asyncio.ensure_future(self.handle_bday(user_id, year))

    def parse_date(self, date_str: str) -> datetime.datetime:
        result = None

        try:
            result = datetime.datetime.strptime(date_str, "%m-%d").date().replace(year=1)
        except ValueError:
            pass

        return result

    def load_data(self) -> None:
        with open(BDAY_JSON_PATH, "r") as file:
            self.config = json.load(file)

    def save_data(self) -> None:
        with open(BDAY_JSON_PATH, "w") as file:
            json.dump(self.config, file, indent=4)


def setup(bot: Bot) -> None:
    bot.add_cog(Birthday(bot))
