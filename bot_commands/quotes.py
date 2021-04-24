import requests
import json


class Quotes():

    def today(self):
        response = requests.get("https://zenquotes.io/api/today")
        json_data = json.loads(response.text)
        quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
        return quote

    def random(self):
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = f"{json_data[0]['q']} - **{json_data[0]['a']}**"
        return quote
