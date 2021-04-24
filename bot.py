import discord
import os
import datetime
import random
import pymongo
from time import sleep
from discord.ext import tasks, commands
from dotenv import load_dotenv

from bot_commands import WordOfTheDay, Quotes

load_dotenv()

token = os.getenv("TOKEN")
wotdChannel = 797553258478305321  # test server
# wotdChannel = 720052365939572748  # normal server

bot = commands.Bot(command_prefix="*")
botLink = "https://discord.com/oauth2/authorize?client_id=738653577693888542&permissions=85072&scope=bot"

colors = (0x00ffff, 0x9fe2bf, 0xccccff, 0xdfff00, 0xf08080, 0xeb984e)

quotes = Quotes()

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
async def word(ctx):
    """Send word of the day."""

    _word = wotd()
    await ctx.send(embed=_word)
    print("word sent")


@bot.command()
async def today(ctx):
    """Sends today's quote."""

    quote = quotes.today()
    await ctx.send(quote)
    print("Today's quote sent.")


@bot.command(name="random")
async def rand(ctx):
    """Sends a random quote."""

    quote = quotes.random()
    await ctx.send(quote)
    print("Random quote sent.")


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


@bot.command()
async def setup(ctx, _channel, _time="08:00"):
    """Setup Word of the Day channel
    and the time in which it gets posted."""

    chan = discord.utils.get(ctx.guild.text_channels, name=_channel)
    if chan == None:
        await ctx.send(f"The channel given does not exist. Try to send a valid channel.")
    else:
        await ctx.send(f"Word of the day will be sent to <#{chan.id}> at {_time}")


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


def wotd():
    color = random.choice(colors)

    (word, currentday, pronounciation,
     wordType, definition, example) = WordOfTheDay.scrape()

    wordofDay = discord.Embed(
        title=f"{word} | {currentday}", color=color)
    wordofDay.set_footer(text="Word of the Day")
    wordofDay.add_field(
        name="Pronounciation", value=pronounciation, inline=False)
    wordofDay.add_field(
        name="Word type", value=f"*{wordType}*", inline=False)
    wordofDay.add_field(
        name="Definition", value=definition, inline=False)
    wordofDay.add_field(
        name="Example", value=example, inline=False)
    return wordofDay


init_wotd.start()
bot.run(token)
