import discord
import os
import datetime
import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from discord.ext import tasks
from urllib.request import urlopen
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()
token = os.getenv("TOKEN")
# wotdChannel = 797553258478305321  # test server
wotdChannel = 720052365939572748  # normal server

botLink = "https://discord.com/oauth2/authorize?client_id=738653577693888542&permissions=85072&scope=bot"


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('*word'):
        wordofDay = wordOfTheDay()
        await message.channel.send(embed=wordofDay)
        print("Word of the day sent.")

    if message.content.startswith('*today'):
        quote = todayQuote()
        await message.channel.send(quote)
        print("Today's quote sent.")

    if message.content.startswith('*random'):
        quote = RandomQuote()
        await message.channel.send(quote)
        print("Random quote sent.")

    if message.content.startswith('*invite'):
        await message.channel.send(botLink)
        print("bot link sent.")


@tasks.loop(hours=24)
async def wotd():
    msgChannel = client.get_channel(wotdChannel)
    print(f"Got channel {msgChannel}")
    wordofDay = wordOfTheDay()
    await msgChannel.send(embed=wordofDay)


@wotd.before_loop
async def before():
    await client.wait_until_ready()
    print("Waiting for time to post")
    while True:
        now = datetime.datetime.now()
        if f"{now.hour:02d}:{now.minute:02d}" == "8:00":
            break
        sleep(60)

    print("Finished waiting")


def wordOfTheDay():
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

    wordofDay = discord.Embed(
        title=f"{word} | {currentday}", color=0x00ffff)
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


def todayQuote():
    response = requests.get("https://zenquotes.io/api/today")
    json_data = json.loads(response.text)
    quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
    return quote


def RandomQuote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
    return quote


wotd.start()
client.run(token)
