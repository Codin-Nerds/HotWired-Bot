import random as r
from discord.ext import commands
from bot.utils.jobfinder import DiscordJobFinder


class Jobs(commands.Cog):
    @commands.command()
    async def job_find(self, ctx: commands.Context, amount=3):
        """Searches for jobs at discord."""
        await ctx.send(f"Searching for {amount} jobs...".)

        finder = DiscordJobFinder()

        jobs = finder.jobs
        r.shuffle(jobs)

        for job in jobs[:amount]:
            await ctx.send(embed=job.embed())


def setup(bot):
    bot.add_cog(Jobs(bot))
