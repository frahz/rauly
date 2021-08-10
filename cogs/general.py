import asyncio
import discord
from discord import guild
import pymongo
import os
from configparser import ConfigParser
from discord.ext import commands, tasks


class General(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.ini_path = os.path.join(os.getcwd(), 'config.ini')
        self.config = ConfigParser()
        self.config.read(self.ini_path)

        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo["discord-bot"]
        self.collection = self.db["guilds"]

        self.guild_id = int(self.config["TEST"]["GUILD_ID"])

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(self.guild_id)

    @commands.command()
    async def invite(self, ctx: commands.Context, elevated=None):
        """Invite the bot to your server.

        add 'elevated' or 'e' to get a bot with higher permissions.
        """

        if elevated == None:
            perm = discord.Permissions(permissions=85072)
        elif elevated in ("elevated", "e"):
            perm = discord.Permissions(permissions=138781519056)
        else:
            await ctx.send("The argument given is not valid, try again")
            return

        botLink = discord.utils.oauth_url(self.bot.user.id, permissions=perm)
        await ctx.send(botLink)
        print("bot link sent.")

    @commands.command(name="find")
    async def find(self, ctx: commands.Context):
        """Debugging database"""
        for item in self.collection.find():
            print(item)



def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
