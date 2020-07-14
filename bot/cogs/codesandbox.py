import asyncio
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord import Forbidden, HTTPException
from discord.ext.commands import Cog, CommandError, Context, command, is_owner

from bot.core.bot import Bot


class CodeSandbox(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._last_eval_result = None

    def _clean_code(self, code: str) -> str:
        if code.startswith("```") and code.endswith("```"):
            return "\n".join(code.split("\n")[1:-1])
        return code.strip("`\n")

    @is_owner()  # TODO: Change this to use custom check
    @command(name="eval", hidden=True)
    async def _eval(self, ctx: Context, *, code: str) -> None:
        """Evaluate the passed code."""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "guild": ctx.guild,
            "channel": ctx.channel,
            "author": ctx.author,
            "message": ctx.message,
            "_": self._last_eval_result,
        }
        env.update(globals())

        code = self._clean_code(code)
        buffer = io.StringIO()

        # function placeholder
        to_compile = f'async def codefn():\n{textwrap.indent(code, " ")}'

        try:
            exec(to_compile, env)  # TODO: Very unsafe
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n``")

        codefn = env["codefn"]
        try:
            with redirect_stdout(buffer):
                ret = await codefn()
        except Exception:
            value = buffer.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = buffer.getvalue()
            await ctx.message.add_reaction("\N{INCOMING ENVELOPE}")

            if not ret:
                if value is not None:
                    await ctx.send(f"```py\n{value}\n```")
                else:
                    self._last_result = ret
                    await ctx.send(f"```py\n{value}{ret}\n```")

    @command(pass_context=True, hidden=True)
    @is_owner()
    async def repl(self, ctx: Context) -> None:
        """Launches an interactive REPL session."""

        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            raise CommandError(message=f'Error: duplicate REPL session in `{ctx.channel.name}`.')

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(m) -> bool:
            return m.author.id == ctx.author.id and \
                m.channel.id == ctx.channel.id and \
                m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()

                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except Forbidden:
                pass
            except HTTPException as e:
                raise CommandError(message=f'Unexpected error: `{e}`')


def setup(bot: Bot) -> None:
    bot.add_cog(CodeSandbox(bot))
