import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen


class WordOfTheDay():

    def scrape():
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
