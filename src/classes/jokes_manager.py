"""
Gets jokes from the Joke API using the requests library
"""

import requests

class Jokes:
    def __init__(self):
        self.base_url = "https://v2.jokeapi.dev/joke"

    def get_joke(self):
        res = requests.get(f"{self.base_url}/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit")
        joke = res.json()

        if joke["error"]:
            return "An error occurred. Please try again."

        if joke["type"] == "twopart":
            joke = f"{joke['setup']}\n||{joke['delivery']}||"
        else:
            joke = joke["joke"]

        return joke
