import random

from discord.ext import commands


class Games(commands.Cog):

  def __init__(self, client):
    self.client = client

  #Commands
  @commands.command()
  async def roll(self, ctx, min_limit=1, max_limit=10):
    """
    Roll a random number
    """
    if max_limit - min_limit > 2:
      number = random.randint(min_limit, max_limit)
      await ctx.send('The random number is ' + str(number))
    else:
      await ctx.send('Please specify numbers with difference of **at least 2**')


  @commands.command(aliases=['8ball'])
  async def ball8(self, ctx, *, question):
    """
    Play 8ball
    """
    yes_responses = [
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes."
      ]
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
      ]

    def is_lucky():
      no = random.randint(1, 3)
      if no == 1:
        return True

    if is_lucky():
      answer = random.choice(yes_responses)
    else:
      answer = random.choice(responses)

    await ctx.send(f'Question : {question}\nAnswer : {answer}')

def setup(client):
  client.add_cog(Games(client))
