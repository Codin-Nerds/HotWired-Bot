import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext.commands import Bot, Cog, Context, command, is_owner


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


def setup(bot: Bot) -> None:
    bot.add_cog(CodeSandbox(bot))
