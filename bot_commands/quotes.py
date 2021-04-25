import requests
import json
from discord.ext import commands


class Quotes(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def today(self, ctx):
        """Sends today's quote."""

        response = requests.get("https://zenquotes.io/api/today")
        json_data = json.loads(response.text)
        quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
        await ctx.send(quote)
        print("Today's quote sent.")

    @commands.command()
    async def random(self, ctx):
        """Sends a random quote."""

        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
        await ctx.send(quote)
        print("Random quote sent.")


def setup(bot):
    bot.add_cog(Quotes(bot))
