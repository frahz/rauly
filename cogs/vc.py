import os
from configparser import ConfigParser
import discord
from discord.ext import commands, tasks


class VoiceChannel(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.ini_path = os.path.join(os.getcwd(), 'config.ini')
        self.config = ConfigParser()
        self.config.read(self.ini_path)

        self.guild_id = int(self.config["DEFAULT"]["GUILD_ID"])
        self.vc_id = int(self.config["DEFAULT"]["VC_CATEGORY_ID"])

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(self.guild_id)
        self.category = self.bot.get_channel(self.vc_id)
        print(self.category)

    @commands.command(name="vc")
    async def vc_member_count(self, ctx: commands.Context):
        total_member_count = 0
        for vc in self.category.voice_channels:
            ch_count = len(vc.members)
            if ch_count != 0:
                print(f"name: {vc.name} members: {ch_count}")
            total_member_count += ch_count
        print(f"total peeps in vc: {total_member_count}")


def setup(bot: commands.Bot):
    bot.add_cog(VoiceChannel(bot))
