import datetime
import discord
import random
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib.request import urlopen


class WordOfTheDay(commands.Cog):
    """word of the day commands and setup"""

    colors = (0x00ffff, 0x9fe2bf, 0xccccff, 0xdfff00,
              0xf08080, 0xeb984e, 0xff8b3d, 0xffaf7a)

    def __init__(self, bot) -> None:
        self.bot = bot

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

    @commands.command()
    async def word(self, ctx):
        """Send word of the day."""

        _word = self.wotd()
        await ctx.send(embed=_word)
        print("word sent")

    @commands.command()
    async def setup(self, ctx, _channel, _time="08:00"):
        """Setup Word of the Day channel
        and the time in which it gets posted."""

        chan = discord.utils.get(ctx.guild.text_channels, name=_channel)
        if chan == None:
            await ctx.send(f"The channel given does not exist. Try to send a valid channel.")
        else:
            await ctx.send(f"Word of the day will be sent to <#{chan.id}> at {_time}")


def setup(bot):
    bot.add_cog(WordOfTheDay(bot))
