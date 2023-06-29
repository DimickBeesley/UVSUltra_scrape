import pandas as pd
import re

import time
import csv

from requests_html import HTMLSession
from bs4 import BeautifulSoup




import socket
from urllib3.connection import HTTPConnection

HTTPConnection.default_socket_options = (
    HTTPConnection.default_socket_options + [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.SOL_TCP, socket.TCP_KEEPINTVL, 10),
        (socket.SOL_TCP, socket.TCP_KEEPCNT, 6)
    ]
)




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
    
    card_image = soup.select("div.card_image")    
    #TODO Make sure the return value when we do this is handled in a good way
    print(len(card_image))
    #if (len(card_image) == 0): return

    """
    dictionary = {
        "card_name": card_name[0].text.strip(),
        "random_stuff_1": soup.select("div.card_division.cd1")[0].text.strip(), # I actually don't know what this will be hitting
        "card_text": soup.select("#text")[0].text.strip(),
        "int_values": soup.select("div.card_division.cd3")[0].text.strip()
    }
    """
    
    return #dictionary

used_ids = []

for i in range(0,13000):
    response = request_card_w_id("1", session).text
    temp_soup = BeautifulSoup(response, 'html.parser')
    temp = temp_soup.select("div.card_image")
    if len(temp) == 0:
        used_ids.append(0)
    if len(temp) == 1:
        used_ids.append(1)
    if len(temp) > 1:
        used_ids.append(2)

print(used_ids)


"""
print(dictionary["card_name"])
print(dictionary["random_stuff_1"])
print(dictionary["card_text"])
print(dictionary["int_values"])
"""