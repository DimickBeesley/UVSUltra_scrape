import pandas as pd
import re

from requests_html import HTMLSession
from bs4 import BeautifulSoup


session = HTMLSession()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
base_url = "https://www.uvsultra.online"
showcard_url = "/showcard.php?id="

""" Pass the id in as a string for the sake of typing issues and your sanity.
    This requests all of the relevant data from an individual card.
"""
def request_card_w_id(id, sesh):
    
    request_url = base_url + showcard_url + id
    response = sesh.get(request_url)

    return response

""" Calls request_card_w_id for every id in some crafted list of ids 
"""
def request_cards_w_ids(list_of_ids, sesh):

    list_o_returns = []

    for id in list_of_ids:
        # Might want to make sure that it is clear that we need to be passing strings into this call
        current = request_card_w_id(id, sesh)
        if (current == None): continue
        list_o_returns.append(current)

    return list_o_returns

""" Take in a response return the card data parsed out. Skip responses that don't actually contain card data.
"""
def parse_soup(response):

    soup = BeautifulSoup(response.text, 'html.parser')
    
    card_name = soup.select("div.card_title h1")    
    #TODO Make sure the return value when we do this is handled in a good way
    if (len(card_name) == 0): return

    dictionary = {
        "card_name": card_name[0].text.strip(),
        "random_stuff_1": soup.select("div.card_division.cd1")[0].text.strip(), # I actually don't know what this will be hitting
        "card_text": soup.select("#text")[0].text.strip(),
        "int_values": soup.select("div.card_division.cd3")[0].text.strip()
    }
    
    return dictionary

response = request_card_w_id("1", session)
dictionary = parse_soup(response)

print(dictionary["card_name"])
print(dictionary["random_stuff_1"])
print(dictionary["card_text"])
print(dictionary["int_values"])