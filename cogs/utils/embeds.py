import asyncio
import re
from functools import partial

import discord
from discord.ext import commands


class BaseEmbeds:
    def __init__(self, ctx, content, color=discord.Color.default(),
                 title="This is my Game", footer=None, thumbnail=None, image=None):
        self.ctx = ctx
        self.author = ctx.author
        self.content = content
        self.message = None

        self.emb = discord.Embed(title=title, color=color)
        self.instance = True

        self.react_controls = [("\N{BLACK SQUARE FOR STOP}", self.stop)]

    def invoker(self, reaction):
        if reaction.user_id != self.author.id or reaction.message_id != self.message.id:
            return False
        for react_controls, functionality in self.react_controls:
            if str(reaction.emoji) == react_controls:
                self.control_function = functionality
                return True

    async def get_content(self):
        return self.content

    async def outfit_embed(self, information):
        self.emb.description = information
        return self.emb

    async def cancel(self):
        if self.message:
            try:
                await self.message.delete()
            except (discord.errors.Forbidden, discord.NotFound):
                pass
        self.controller_task.cancel()
        self.instance = False

    async def stop(self, *args):
        await self.cancel()

    async def embed_controller(self, create=False):
        content_info = await self.get_content()
        self.emb = await self.outfit_embed(content_info)

        if create is False:
            try:
                await self.message.edit(embed=self.emb)
            except discord.Forbidden:
                raise commands.BotMissingPermissions("Embed Links!")
        else:
            try:
                self.message = await self.ctx.send(embed=self.emb)
            except discord.Forbidden:
                raise commands.BotMissingPermissions("Embed Links!")

            if self.message is None or not self.message.embeds:
                return

            for user_input_buttons in self.react_controls:
                try:
                    await self.message.add_reaction(user_input_buttons[0])
                except (discord.NotFound, discord.Forbidden):
                    pass

    async def start(self):
        self.controller = self.embed_controller(create=True)

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.controller)

        while self.instance:
            try:
                control = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=10)
            except asyncio.TimeoutError:
                self.instance = False
                self.controller_task.cancel()
                if self.message:
                    try:
                        await self.message.delete()
                    except (discord.errors.Forbidden, discord.NotFound):
                        pass
                break

            try:
                await self.message.remove_reaction(control.emoji, discord.Object(id=control.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass
            try:
                await self.control_function()
            except AttributeError:
                return False


# Paged Embeds
class PagedEmbed(BaseEmbeds):
    def __init__(self, ctx, content, color=discord.Color.default(),
                 title="Placeholder Title", over_or_underflow=True, display_page=False, fields: dict = None):
        """Initializes and controls a embed with pagination."""
        super().__init__(ctx, content, color=discord.Color.default(), title="Placeholder Title")

        self.over_or_under = over_or_underflow
        self.display_page = display_page
        self.current_page = 0
        self.max_pg = len(content) - 1

        self.emb = discord.Embed(title=title, color=color)
        if fields:
            for name, value in fields.items():
                self.emb.add_field(name=name, value=value)

        if self.max_pg > 0:
            self.react_controls = [
                ("\N{BLACK LEFT-POINTING TRIANGLE}", self.prev_page),
                ("\N{BLACK SQUARE FOR STOP}", self.stop),
                ("\N{BLACK RIGHT-POINTING TRIANGLE}", self.next_page),
                ("📄", self.goto)]
        else:
            self.react_controls = []

    def invoker(self, reaction):
        if reaction.user_id != self.author.id or reaction.message_id != self.message.id:
            return False

        for emote, functionality in self.react_controls:
            if str(reaction.emoji) == emote:
                self.control_function = functionality
                return True
        return False

    async def next_page(self, *args):
        self.current_page += 1

        if self.current_page > self.max_pg and self.over_or_under is True:
            self.current_page = 0
        elif self.current_page > self.max_pg and self.over_or_under is False:
            self.current_page = self.max_pg

        await self.embed_controller()

    async def prev_page(self, *args):
        self.current_page -= 1

        if self.current_page < 0 and self.over_or_under is True:
            self.current_page = self.max_pg
        elif self.current_page < 0 and self.over_or_under is False:
            self.current_page = 0

        await self.embed_controller()

    async def goto(self, *args):
        def check(convert):
            try:
                convert = int(convert)
                return 1
            except ValueError:
                if re.match("exit", convert):
                    return 2

        get_page = await self.ctx.get_response("Please select a page number to go to")
        if get_page and check(get_page[0].content) is 1:
            page_to_go = int(get_page[0].content)
            if page_to_go > self.max_pg+1 or page_to_go < 0:
                await self.ctx.send("Invalid page number!", delete_after=5)
            else:
                self.current_page = page_to_go-1 if page_to_go > 0 else 0
        elif get_page is None:
            return

        await self.embed_controller()
        await self.ctx.group_delete(*get_page)

    async def get_content(self):
        return self.content[self.current_page]

    async def outfit_embed(self, information):
        self.emb.description = information

        if self.display_page is True:
            page = f"\n{self.current_page + 1}/{self.max_pg + 1}"
            self.emb.set_footer(text=page)

        return self.emb


class ConfirmEmbed(PagedEmbed):
    def __init__(self, ctx, content, color=discord.Color.default(), title="Placeholder Title"):
        super().__init__(ctx, content, color, title)

        if self.max_pg > 0:
            self.react_controls = [emote for emote in self.react_controls]
        else:
            self.react_controls = [("\N{BLACK SQUARE FOR STOP}", self.stop)]

        self.react_controls += [("✅", self.yes), ("🚫", self.no)]

    async def yes(self):
        await self.cancel()
        return True

    async def no(self):
        await self.cancel()
        return False

    async def start(self):
        self.caller = self.embed_controller(create=True)  # Begins

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.caller)
        while self.instance:
            try:
                self.command = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=60)
            except asyncio.TimeoutError:
                await self.cancel()
                break
            try:
                await self.message.remove_reaction(self.command.emoji, discord.Object(id=self.command.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass

            try:
                returned_search = await self.control_function()
            except AttributeError:
                returned_search = None
            if isinstance(returned_search, bool):
                return returned_search


class ConfirmEmbedAnother(PagedEmbed):
    def __init__(self, ctx, user, content, color=discord.Color.default(), title="Placeholder Title", dm=False):
        super().__init__(ctx, content, color, title)
        self.author = user
        self.dm = dm

        if self.max_pg > 0:
            self.react_controls = [emote for emote in self.react_controls]
        else:
            self.react_controls = [("\N{BLACK SQUARE FOR STOP}", self.stop)]

        self.react_controls += [("✅", self.yes), ("🚫", self.no)]

    def invoker(self, reaction):
        if reaction.user_id != self.author.id or reaction.message_id != self.message.id:
            return False

        for emote, functionality in self.react_controls:
            if str(reaction.emoji) == emote:
                self.control_function = functionality
                return True
        return False

    async def embed_controller(self, create=False):
        content_info = await self.get_content()
        self.emb = await self.outfit_embed(content_info)

        if create is False:
            try:
                await self.message.edit(embed=self.emb)
            except discord.Forbidden:
                raise commands.BotMissingPermissions("Embed Links!")
        else:
            try:
                if self.dm is False:
                    self.message = await self.ctx.send(embed=self.emb)
                else:
                    self.message = await self.author.send(embed=self.emb)

                if self.message is None or not self.message.embeds:
                    return
            except discord.Forbidden:
                self.instance = False
                return await self.ctx.send(f"I don't have the permission to send Embeds and/or can't DM {self.author.name}")

            for user_input_buttons in self.react_controls:
                try:
                    await self.message.add_reaction(user_input_buttons[0])
                except (discord.NotFound, discord.Forbidden):
                    pass

    async def yes(self):
        await self.cancel()
        return True

    async def no(self):
        await self.cancel()
        return False

    async def start(self):
        self.caller = self.embed_controller(create=True)  # Begins

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.caller)
        while self.instance:
            try:
                self.command = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=15)
            except asyncio.TimeoutError:
                await self.cancel()
                break
            try:
                await self.message.remove_reaction(self.command.emoji, discord.Object(id=self.command.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass

            try:
                confirm_result = await self.control_function()
            except AttributeError:
                confirm_result = None
            if isinstance(confirm_result, bool):
                return confirm_result
        return None


class NumberedChooserPager(PagedEmbed):
    def __init__(self, ctx, content, color=discord.Color.default(), title="Placeholder Title", select_emojis_list=None):
        super().__init__(ctx, content, color, title)

        if self.max_pg > 0:
            self.react_controls = [emote + (None,) for emote in self.react_controls]
        else:
            self.react_controls.clear()

        for assigned_result, emote in enumerate(select_emojis_list):
            self.react_controls.append((emote, self.answer, assigned_result))

        if self.max_pg == 0:
            self.react_controls.append(("\N{BLACK SQUARE FOR STOP}", self.stop, None))

    async def answer(self, selected):
        await self.cancel()
        return selected

    def invoker(self, reaction, *args):

        if reaction.user_id != self.author.id or reaction.message_id != self.message.id:
            return False

        valid = str(reaction.emoji)

        for emote, functionality, chosen_search in self.react_controls:
            if valid == emote:
                self.control_function = partial(functionality, chosen_search)
                return True
        return False

    async def start(self):
        self.caller = self.embed_controller(create=True)  # Begins

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.caller)
        while self.instance:
            try:
                self.command = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=60)
            except asyncio.TimeoutError:
                self.instance = False
                self.controller_task.cancel()
                if self.message:
                    try:
                        await self.message.delete()
                    except (discord.errors.Forbidden, discord.NotFound):
                        pass
                break

            try:
                await self.message.remove_reaction(self.command.emoji, discord.Object(id=self.command.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass

            try:
                returned_search = await self.control_function()
            except AttributeError:
                returned_search = None

            if isinstance(returned_search, int):
                return returned_search


class InputChooserPager(PagedEmbed):
    def __init__(self, ctx, content, possible_choices, color=discord.Color.default(), title="Placeholder Title"):
        super().__init__(ctx, content, color, title)
        if self.max_pg > 0:
            self.react_controls = [
                ("🔢", self.choose),
                ("\N{BLACK LEFT-POINTING TRIANGLE}", self.prev_page),
                ("\N{BLACK SQUARE FOR STOP}", self.stop),
                ("\N{BLACK RIGHT-POINTING TRIANGLE}", self.next_page),
                ("📄", self.goto)]
        else:
            self.react_controls = [("🔢", self.choose), ("\N{BLACK SQUARE FOR STOP}", self.stop)]
        self.possible_choices = possible_choices

        # As the instance variable "react_emoji" is inherited from the parent PagedEmbed class, it would be by default
        # Filled with the page and stop button. However as for this varient of the embed class it would be likely that
        # there would only be one page. Therefore if self.max_pg (len(content) - 1) is less than or equal to 0
        # meaning one page, then there would be no need for the reaction emojis. Therefore they would get replaced

    async def choose(self):
        def check(convert):
            try:
                convert = int(convert)
                return 1
            except ValueError:
                if re.match("exit", convert):
                    return 2

        get_choice = await self.ctx.get_response("Which one would you like to select? ")
        if get_choice and check(get_choice[0].content):
            choice = int(get_choice[0].content)
            if choice < self.possible_choices:
                await self.ctx.send("Invalid choice number!", delete_after=5)
            else:
                return choice
        elif get_choice is None:
            return

        await self.embed_controller()
        await self.ctx.group_delete(*get_choice)

    async def start(self):
        self.controller = self.embed_controller(create=True)  # Begins

        if self.instance:
            self.controller_task = self.ctx.bot.loop.create_task(self.controller)
        while self.instance:
            try:
                self.command = await self.ctx.bot.wait_for("raw_reaction_add", check=self.invoker, timeout=60)
            except asyncio.TimeoutError:
                await self.cancel()

            try:
                await self.message.remove_reaction(self.command.emoji, discord.Object(id=self.command.user_id))
            except (discord.NotFound, discord.Forbidden):
                pass

            try:
                returned_search = await self.control_function()
            except AttributeError:
                returned_search = None

            if isinstance(returned_search, int):
                return returned_search
