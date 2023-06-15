import pandas as pd
import re

from requests import HTMLSession
from bs4 import BeautifulSoup


session = HTMLSession()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
base_url = "https://www.uvsultra.online"
showcard_url = "showcard.php?id="

""" Pass the id in as a string for the sake of typing issues and your sanity.
    This requests all of the relevant data from an individual card.
"""
def request_card_w_id(id, sesh):
    
    request_url = base_url + showcard_url + id
    r = sesh.get()
    
    return r

def request_cards_w_ids(list_of_ids, sesh):

    list_o_returns = []

    for id in list_of_ids:
        current = request_card_w_id(id, sesh)
        if (current == None): continue
        list_o_returns.append(current)

    return list_o_returns



