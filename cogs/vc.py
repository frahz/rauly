import os
import discord
import pymongo
import pytz
from configparser import ConfigParser
from datetime import datetime
from discord.ext import commands, tasks


class VoiceChannel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.ini_path = os.path.join(os.getcwd(), 'config.ini')
        self.config = ConfigParser()
        self.config.read(self.ini_path)

        self.guild_id = int(self.config["DEFAULT"]["GUILD_ID"])
        self.vc_id = int(self.config["DEFAULT"]["VC_CATEGORY_ID"])

        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo["discord-bot"]
        self.collection = self.db["vc-stats"]

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.guild: discord.Guild = self.bot.get_guild(self.guild_id)
        self.category: discord.CategoryChannel = self.bot.get_channel(
            self.vc_id)
        print(self.category)

    @commands.command(name="vc")
    async def vc_member_count(self, ctx: commands.Context):
        total_member_count = 0
        for vc in self.category.voice_channels:
            ch_count = len(vc.members)
            if ch_count != 0:
                print(f"name: {vc.name} members count: {ch_count}")
            total_member_count += ch_count
        print(f"total peeps in vc: {total_member_count}")

        # channel_data = {}
        # for vc in self.category.voice_channels:
        #     channel_data[vc.name] = len(vc.members)
        #     ch_count = len(vc.members)
        #     total_member_count += ch_count
        # print(channel_data)

    @tasks.loop(hours=1)
    async def vc_logs(self):
        eastern = pytz.timezone("US/Eastern")
        total_member_count = 0
        channel_data = {}

        for vc in self.category.voice_channels:
            channel_data[vc.name] = len(vc.members)
            ch_count = len(vc.members)
            total_member_count += ch_count

        payload = {
            "time": datetime.now(eastern),
            "member_count": total_member_count
        }


def setup(bot: commands.Bot):
    bot.add_cog(VoiceChannel(bot))
