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

""" Retrieves ids from premade file.
"""
def get_ids():

    existing_ids = []
    f = open("uvs_ids.txt", "r")
    id_file = f.readlines()

    for line in id_file:
        existing_ids.append(int(line.strip()))

    f.close()

    return existing_ids


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






def parse_card_info(soup):
    
    """ BREAK UP THE RAW HTML INTO BITES SIZED PIECES """

    # Raw Html
    card_name = soup.select("div.card_infos h1")[0].text
    card_image_src = soup.select("div.card_image img")[0]["src"]

    #The different card divisions from the raw HTML
    card_divisions = soup.select("div.card_infos div.card_division")
    
    #Set/Card number, Card type, Rarity, Format???
    card_division_1 = card_divisions[0].text.strip()  
    #Functionality of the card (enhances, responses, etc.)
    card_division_2 = card_divisions[1].text.strip() 
    #Contol, block mod, attack or not???, Hand size, Vitality
    card_division_3 = card_divisions[2].text.strip()

    # Different pieces of information from card division parsed and thrown into string arrays
    cd1_parsed = parse_card_division(card_division_1)
    for i in range(0, 3):
        cd1_parsed.remove(cd1_parsed[-1])

    cd2_parsed = parse_card_division(card_division_2)
    cd2_parsed[0:-1] = ["/".join(cd2_parsed[0:-1])]

    cd3_parsed = parse_card_division(card_division_3)

    

    # Symbols
    card_symbols_html = soup.select("div.card_infos img")
    card_symbols = ""
    for symbol in card_symbols_html:
        card_symbols += symbol["alt"] + "/"
    card_symbols = card_symbols[0:-1]

    hand_size = ""
    vitality = ""

    if len(cd3_parsed) == 5:
        hand_size = cd3_parsed[4].split(":")[1].strip()[0]
        vitality = cd3_parsed[4].split(":")[2].strip()[-2:]
    # get card type
    card_type = cd1_parsed[1] # set card type
    
    attack_info = cd3_parsed[3].split(":")[1].strip()
    speed = "none"
    zone = "none"
    damage = "none"

    if attack_info != "/":
        speed = attack_info.split(" ")[0]
        zone = attack_info.split(" ")[1]
        damage = attack_info.split(" ")[3]

    """ HANDLE INFORMATION BASED ON CARD TYPE """

    card = {
        "name"       : card_name,
        "image"      : card_image_src,
        "set-info"   : cd1_parsed[0],
        "type"       : cd1_parsed[1],
        "rarity"     : cd1_parsed[2],
        "legality"   : cd1_parsed[3],
        "abilities"  : cd2_parsed[0],
        "errata"     : cd2_parsed[1],
        "control"    : cd3_parsed[0].split(":")[1].strip(),
        "difficulty" : cd3_parsed[1].split(":")[1].strip(),
        "block"      : cd3_parsed[2].split(":")[1].strip(),
        "speed"      : speed,
        "zone"       : zone,
        "damage"     : damage,
        "hand-size"  : hand_size,
        "vitality"   : vitality,
        "symbols"    : card_symbols
    }

    return card

def parse_card_division(card_division):
    split = card_division.split("\n")
    
    while "" in split:
        split.remove("")

    for item in range(0, len(split)):
        split[item] = split[item].strip()

    return split


def handle_character():
    return

def handle_attach():
    return

def handle_other():
    return







id_list = get_ids()
id_iteration = 0

for i in range(0, 100):
    response = request_card_w_id(str(id_list[-i]), session).text
    temp_soup = BeautifulSoup(response, 'html.parser')

    card_dict = parse_card_info(temp_soup)

    for key in card_dict:
        value = card_dict[key]
        print("{k}: {v}".format(k = key, v = value))

    print("\n")


"""
for id in id_list:
    id_iteration += 1
    response = request_card_w_id(str(id), session).text
    temp_soup = BeautifulSoup(response, 'html.parser')
    temp = temp_soup.select("div.card_infos")

    print("exiting iteration #{itr}".format(itr = id_iteration))
"""
