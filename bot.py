import discord
import os
import pymongo
from configparser import ConfigParser
from discord.ext import commands


config = ConfigParser()
config.read("config.ini")

token = config["DEFAULT"]["DISCORD_TOKEN"]

bot = commands.Bot(command_prefix="*")

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

botLink = "https://discord.com/oauth2/authorize?client_id=738653577693888542&permissions=85072&scope=bot"

colors = (0x00ffff, 0x9fe2bf, 0xccccff, 0xdfff00,
          0xf08080, 0xeb984e, 0xff8b3d, 0xffaf7a,
          0xf8b195, 0xf67280, 0xcd6c84, 0x6c587b,
          0x355c7d, 0xa8e6ce, 0xff8c94)


# database info
mongo = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo["discord-bot"]
collection = db["guilds"]


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

    payload = {
        "setup": False,
        "guild": str(guild),
        "guild_id": guild.id,
        "wotd_channel": None,
        "wotd_channel_id": None,
        "wotd_time": None
    }

    add_to_collection = collection.insert_one(payload)
    print(f"added guild: {guild} with guild_id: {guild.id}")


@bot.event
async def on_guild_remove(guild):
    del_from_collection = collection.delete_one({"guild_id": guild.id})
    print(f"bot has been removed from {guild} with guild_id: {guild.id}.")


@bot.command()
async def invite(ctx):
    """Invite the bot to your server."""

    await ctx.send(botLink)
    print("bot link sent.")


@bot.command(name="find")
async def find(ctx):
    """Debugging database"""
    for item in collection.find():
        print(item)


bot.run(token)
