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

        self.guild_id = int(self.config["DEFAULT"]["GUILD_ID"])

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

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def timeout(self, ctx: commands.Context, member: discord.Member, _time: int = 5):
        """"Timeout user for certain amount of time(default is 5 minutes)."""

        await ctx.send(f"user: {member.mention} has been timed out for {_time} minutes.")

        timeout_role = discord.utils.get(self.guild.roles, name="timeout")
        secs = _time * 60

        await member.add_roles(timeout_role)
        await asyncio.sleep(secs)
        await member.remove_roles(timeout_role)
        await ctx.send(f"user {member.mention}'s time out has expired.")

    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        """"Untimeout a member that is currently timed out before their timeout expires"""

        timeout_role = discord.utils.get(self.guild.roles, name="timeout")

        if timeout_role in member.roles:
            await member.remove_roles(timeout_role)
            await ctx.send(f"user: {member.mention} has been untimed out.")
        else:
            await ctx.send(f"user: {member.mention} is not currently timed out.")


def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
