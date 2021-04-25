import discord
import os
import datetime
import pymongo
from configparser import ConfigParser
from time import sleep
from discord.ext import tasks, commands


config = ConfigParser()
config.read("config.ini")

wotdChannel = 797553258478305321  # test server
# wotdChannel = 720052365939572748  # normal server

token = config["DEFAULT"]["DISCORD_TOKEN"]

bot = commands.Bot(command_prefix="*")
bot.load_extension("bot_commands.quotes")
bot.load_extension("bot_commands.word_of_the_day")

botLink = "https://discord.com/oauth2/authorize?client_id=738653577693888542&permissions=85072&scope=bot"

colors = (0x00ffff, 0x9fe2bf, 0xccccff, 0xdfff00,
          0xf08080, 0xeb984e, 0xff8b3d, 0xffaf7a)


# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["discord-bot"]
# collection = db["guilds"]


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_guild_join(guild):
    success = False
    i = 0
    while not success:
        try:
            await guild.channels[i].send("Thanks for the server invite. If you wish to set up the Word of the Day, please run `*setup <channel> <time>` to get it up and running.")
        except (discord.Forbidden, AttributeError):
            i += 1
        except IndexError:
            pass
        else:
            success = True


@bot.command()
async def invite(ctx):
    """Invite the bot to your server."""

    await ctx.send(botLink)
    print("bot link sent.")


@bot.command()
async def channel(ctx, _channel):
    chan = discord.utils.get(ctx.guild.text_channels, name=_channel)
    print(
        f"got channel {chan} with channel id {chan.id} and type {type(chan)}.")


@tasks.loop(hours=24)
async def init_wotd():
    msgChannel = bot.get_channel(wotdChannel)
    print(f"Got channel {msgChannel}")
    word = wotd()
    await msgChannel.send(embed=word)


@init_wotd.before_loop
async def before():
    await bot.wait_until_ready()
    print("Waiting for time to post")
    while True:
        now = datetime.datetime.now()
        print(f"{now.hour:02d}:{now.minute:02d}")
        if f"{now.hour:02d}:{now.minute:02d}" == "13:00":
            break
        sleep(60)

    print("Finished waiting")


# init_wotd.start()
bot.run(token)
