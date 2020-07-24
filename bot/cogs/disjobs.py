import random as r
from discord.ext import commands
from bot.utils.jobfinder import DiscordJobFinder

class Jobs(commands.Cog):
    @commands.command(name="job-find", help="Searches for jobs at discord.")
    async def job_find(self, ctx, amount=3):
        await ctx.send('Searching for {} jobs...'.format(amount))

        finder = DiscordJobFinder()

        jobs = finder.jobs
        r.shuffle(jobs)

        for job in jobs[:amount]:
            await ctx.send(embed=job.embed())


def setup(bot):
    bot.add_cog(Jobs(bot))
