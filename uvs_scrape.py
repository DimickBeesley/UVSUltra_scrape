# For making requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

# Preventing connection issues from stopping the script
import socket
from urllib3.connection import HTTPConnection

# Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import json_util


# Functionally, constants for connecting to Mongodb
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = "dotdeck"
COLLECTION_NAME = "uvscards"

# Some black magic that helps keep the connection from dropping while the script scrapes
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

""" Calls request_card_w_id for every id in some crafted list of ids to return a list of responses
"""
def request_cards_w_ids(list_of_ids, sesh):

    list_o_returns = []

    for id in list_of_ids:
        # Might want to make sure that it is clear that we need to be passing strings into this call
        current = request_card_w_id(id, sesh)
        if (current == None): continue
        list_o_returns.append(current)

    return list_o_returns

""" Takes in the soup. Returns the information as a dictionary
"""
def parse_card_info(soup):
    
    """ BREAK UP THE RAW HTML FOR EASIER PARSING 
    """

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



    """ TURN THE RAW DATA INTO VARIABLES WE CAN POPULATE A DICTIONARY WITH 
    """

    # Variables for populating the dict we'll return
    hand_size = "none"
    vitality = "none"
    attack_info = cd3_parsed[3].split(":")[1].strip()
    speed = "none"
    zone = "none"
    damage = "none"
    card_type = cd1_parsed[1] # set card type
    card_symbols_html = soup.select("div.card_infos img")
    card_symbols = ""
    
    # handles the seperate img tags to get the symbols
    for symbol in card_symbols_html:
        card_symbols += symbol["alt"] + "/"
    card_symbols = card_symbols[0:-1]

    # handles character information if character
    if len(cd3_parsed) == 5:
        hand_size = cd3_parsed[4].split(":")[1].strip()[0]
        vitality = cd3_parsed[4].split(":")[2].strip()[-2:]
    
    # handles attack information if attack
    if attack_info != "/":
        speed = attack_info.split(" ")[0]
        zone = attack_info.split(" ")[1]
        damage = attack_info.split(" ")[3]


    """ POPULATE THE DICTIONARY FOR RETURN
    """

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


""" Breaks up some of the information that came in bigger chunks inside of the raw html
"""
def parse_card_division(card_division):
    split = card_division.split("\n")
    
    while "" in split:
        split.remove("")

    for item in range(0, len(split)):
        split[item] = split[item].strip()

    return split





""" Funtionally, the main function
"""

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

