import asyncio
import datetime
import discord
from discord.ext.commands.core import Command
import pymongo
import random
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
from urllib.request import urlopen


class WordOfTheDay(commands.Cog):
    """word of the day commands and setup"""

    colors = (0x00ffff, 0x9fe2bf, 0xccccff, 0xdfff00,
              0xf08080, 0xeb984e, 0xff8b3d, 0xffaf7a,
              0xf8b195, 0xf67280, 0xcd6c84, 0x6c587b,
              0x355c7d, 0xa8e6ce, 0xff8c94)

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo["discord-bot"]
        self.collection = self.db["guilds"]
        self.init_word.start()

    def scrape(self):
        currentday = datetime.date.today().strftime("%B %d, %Y")

        url = "https://www.dictionary.com/e/word-of-the-day/"
        page = urlopen(url)

        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # word scraping
        worddiv = soup.find(
            "div", {"class": "otd-item-headword__word"})
        word = worddiv.text.strip()

        # pronounciation scraping // needs more work
        pronounciationdiv = soup.find(
            "div", {"class": "otd-item-headword__pronunciation"})
        pronounciation = pronounciationdiv.text.strip()
        boldword = pronounciationdiv.find_all(
            "span", {"class": "bold"})
        italicword = pronounciationdiv.find_all(
            "span", {"class": "italic"})
        # checks if the word is bolded or italicized and sets correct markdown styles
        for i in italicword:
            if i in italicword:
                italicized = f"*{i.text}*"
                pronounciation = pronounciation.replace(i.text, italicized)
        for j in boldword:
            if j in boldword:
                bolded = f"**{j.text}**"
                pronounciation = pronounciation.replace(j.text, bolded)

        # word type and definition scraping
        wordTypeDefinitiondiv = soup.find(
            "div", {"class": "otd-item-headword__pos"})
        wordType = wordTypeDefinitiondiv.find(
            "span", {"class": "luna-pos"}).text
        definition = wordTypeDefinitiondiv("p")[1].text

        # example scraping
        examplediv = soup.find("div", {"class": "wotd-item-example__content"})
        exampleBase = examplediv.text.strip()
        example = exampleBase.replace(word, f"**{word}**")

        return (word, currentday, pronounciation, wordType, definition, example)

    def wotd(self):
        color = random.choice(self.colors)

        (word, currentday, pronounciation,
         wordType, definition, example) = self.scrape()

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

    def seconds_until(self, hours, minutes):
        given_time = datetime.time(hours, minutes)
        now = datetime.datetime.now()
        future_exec = datetime.datetime.combine(now, given_time)
        if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
            future_exec = datetime.datetime.combine(
                now + datetime.timedelta(days=1), given_time)  # days always >= 0

        return (future_exec - now).total_seconds()

    @commands.command(name="word")
    async def send_word(self, ctx: commands.Context):
        """Send word of the day."""

        _word = self.wotd()
        await ctx.send(embed=_word)
        print("word sent")

    @commands.command()
    async def setup(self, ctx: commands.Context, _channel, _time="08:00"):
        """Setup Word of the Day channel
        and the time in which it gets posted."""

        if self.collection.find_one({"guild_id": ctx.guild.id})["setup"] == True:
            await ctx.send(f"The server `{ctx.guild}` already has the word of the day setup.")
            return

        chan = discord.utils.get(ctx.guild.text_channels, name=_channel)
        if chan == None:
            await ctx.send("The channel given does not exist. Try to send a valid channel.")
        else:
            await ctx.send(f"Word of the day will be sent to <#{chan.id}> at {_time}")
            payload = {
                "$set": {
                    "setup": True,
                    "guild": str(chan.guild),
                    "guild_id": chan.guild.id,
                    "wotd_channel": str(chan),
                    "wotd_channel_id": chan.id,
                    "wotd_time": _time
                }
            }
            update_collection = self.collection.update_one(
                {"guild_id": chan.guild.id}, payload)
            print(
                f"updated {chan} from {chan.guild} to the database and it will post at {_time}")

    @tasks.loop(hours=24)
    async def init_word(self):
        for guild in self.collection.find().sort("wotd_time"):
            h = int(guild["wotd_time"][:2])
            m = int(guild["wotd_time"][3:])
            print(f"waiting for {guild['guild']} at {guild['wotd_time']}")
            secs = self.seconds_until(h, m)
            if secs > 86340:  # check to see if the upcoming guild has the same post time as the previous one
                pass
            else:
                await asyncio.sleep(secs)
            channel = await self.bot.fetch_channel(guild["wotd_channel_id"])
            print(f"Got channel {channel}")
            word = self.wotd()
            await channel.send(embed=word)


def setup(bot: commands.Bot):
    bot.add_cog(WordOfTheDay(bot))
