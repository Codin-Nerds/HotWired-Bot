import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext import commands


class CodeSandbox(commands.Cog):

    def __init__(self, client):
        self.client = client
        self._last_eval_result = None

    @commands.command()
    async def code(self, ctx):
        await ctx.send('code working!')

    def _clean_code(self, code):
        if code.startswith('```') and code.endswith('```'):
            return '\n'.join(code.split('\n')[1:-1])
        return code.strip('`\n')

    # TODO : try to restrict to verified users only.
    @commands.is_owner()
    @commands.command(name='eval', hidden=True)
    async def _eval(self, ctx, *, code: str):

        env = {
            'bot': self.client,
            'ctx': ctx,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            'message': ctx.message,
            '_': self._last_eval_result
        }
        env.update(globals())

        code = self._clean_code(code)
        buffer = io.StringIO()

        # function placeholder
        to_compile = f'async def code():\n{textwrap.indent(code, " ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```python\n{e.__class__.__name__}: {e}\n``')

        code = env['code']
        try:
            with redirect_stdout(buffer):
                ret = await code()
        except Exception:
            value = buffer.getvalue()
            await ctx.send(f'```python\n{value}{traceback.format_exc()}\n```')
        else:
            value = buffer.getvalue()
            try:
                await ctx.message.add_reaction('\N{INCOMING ENVELOPE}')
            except Exception:
                pass

            if ret is None:
                if value is not None:
                    await ctx.send(f'```python\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```python\n{value}{ret}\n```')


def setup(client):
    client.add_cog(CodeSandbox(client))
