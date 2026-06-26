import json
import random


def get_character_from_quote(quote):
    with open("data/quotes/characters.json", "r") as f:
        data = json.load(f)["characters"]
    f.close()
    c = quote["character"]
    character = data[c]
    return character


def get_house_from_character(character):
    if  not character["house"]:
        return None
    with open("data/quotes/houses.json", "r") as f:
        data = json.load(f)["houses"]
    f.close()
    house = data[character["house"]]
    return house


class QuotesManager:
    def __init__(self):
        pass

    def get_quote(self):
        with open("data/quotes/quotes.json", "r") as f:
            data = json.load(f)["quotes"]
        f.close()
        quote = random.choice(data)
        print(quote)
        character = get_character_from_quote(quote)
        house = get_house_from_character(character)

        if house:
            res = (f"> {quote['sentence']}\n"
                    f"\\- {character['name']}, {house['name']}")
            return res
        res = (f"> {quote['sentence']}\n"
               f"\\- {character['name']}")
        return res