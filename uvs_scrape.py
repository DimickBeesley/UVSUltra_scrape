#!/usr/bin/env python3

# For making requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

# Preventing connection issues from stopping the script
import socket
from urllib3.connection import HTTPConnection

# JSON
import json


# Functionally, constants for connecting to Mongodb
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = "dotdeck"
COLLECTION_NAME = "uvscards"

# Creating a socket to help keep the connection alive. (Does it mean we're using TCP instead of UDP?)
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
id_file = "uvs_ids.txt"
data_file = "uvs_card_data.json"

#TODO: fix the error that makes this not execute.
def update_ids_file():
    
    with open(id_file, "rb") as file:
        file.seek(-2,2) # move pointer to the second to last byte.
        while file.read(1) != b'\n':
            file.seek(-2,1)
        last_line = file.readline().decode()
        target_id = int(last_line)
    
    target_id = None
    fail_to_find_count = 0

    with open(id_file, "a") as file:
        # this line is the problem. we get a request back no matter what. check the contents of the response here instead.
        while fail_to_find_count >= 100:
            try:
                response = request_card_w_id(target_id, session)
                soup = BeautifulSoup(response, 'html.parser')
                # this throwing an error determines that there is no card with this id
                card_name = soup.select("div.card_infos h1")[0].text
                file.write("/n" + str(target_id))
                print("target_id=" + str(target_id))
                
                target_id = target_id + 1
                fail_to_find_count = 0
            except: 
                fail_to_find_count = fail_to_find_count + 1
                target_id = target_id + 1
                continue


""" Retrieves ids from premade file. """
def get_ids():

    existing_ids = []
    f = open("uvs_ids.txt", "r")
    id_file = f.readlines()

    for line in id_file:
        existing_ids.append(int(line.strip()))

    f.close()

    return existing_ids


""" Pass the id in as a string for the sake of typing issues and your sanity.
    This requests all of the relevant data from an individual card. """
def request_card_w_id(id, sesh):
        

    request_url = base_url + showcard_url + str(id)
    response = sesh.get(request_url)

    return response


""" Calls request_card_w_id for every id in some crafted list of ids to return a list of responses """
def request_cards_w_ids(list_of_ids, sesh):

    list_o_returns = []

    for id in list_of_ids:
        # Might want to make sure that it is clear that we need to be passing strings into this call
        current = request_card_w_id(id, sesh)
        if (current == None): continue
        list_o_returns.append(current)

    return list_o_returns


""" Takes in the soup. Returns the information as a dictionary """
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
    setinfo = ""
    card_type = ""
    card_rarity = ""
    legality = ""

    
    if len(cd1_parsed) > 3:
        setinfo = cd1_parsed[0]
        card_type = cd1_parsed[1]
        card_rarity = cd1_parsed[2]
        legality = cd1_parsed[3]
    else: #exception where card doesn't have a rarity
        setinfo = cd1_parsed[0]
        card_type = cd1_parsed[1]
        card_rarity = "none"
        legality = cd1_parsed[2]

    
    # handles the seperate img tags to get the symbols
    for symbol in card_symbols_html:
        card_symbols += symbol["alt"] + "/"
    card_symbols = card_symbols[0:-1]

    # handles character information if character
    if len(cd3_parsed) == 5:
        hand_size = cd3_parsed[4].split(":")[1].strip()[0]
        vitality = cd3_parsed[4].split(":")[2].strip()[-2:]
    
    # handles attack information if attack

    try:
        if attack_info != "/": 
            '''and len(attack_info.split(" ")) < 3'''
            print(attack_info != "/")
            speed = attack_info.split(" ")[0]
            #print(speed)
            zone = attack_info.split(" ")[1]
            #print(zone)
            damage = attack_info.split(" ")[3]
            #print(damage)
    except:
        speed = zone = damage = "exception"

    """ POPULATE THE DICTIONARY FOR RETURN
    """
    card = {
        "name"       : card_name,
        "image"      : card_image_src,
        "set-info"   : setinfo,
        "type"       : card_type,
        "rarity"     : card_rarity,
        "legality"   : legality,
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


""" Breaks up some of the information that came in bigger chunks inside of the raw html """
def parse_card_division(card_division):
    split = card_division.split("\n")
    
    while "" in split:
        split.remove("")

    for item in range(0, len(split)):
        split[item] = split[item].strip()

    return split


""" Run the script for one id only for the sake of testing mostly """
def parse_card_w_id(target_card_id):
    
    response = request_card_w_id(str(target_card_id), session).text

    temp_soup = BeautifulSoup(response, 'html.parser')
    print(temp_soup.select("div.card_infos"))

    target_card_info = parse_card_info(temp_soup)
    print(target_card_info)
    print("***************")

    return target_card_info


""" Makes calls to the other functions to request all of the card information  
    and save it to a json file in the current directory """
def execute_scrape(id_list, session):
    card_dicts = []
    
    for id in id_list:
        # get the soup
        response = request_card_w_id(str(id), session).text
        temp_soup = BeautifulSoup(response, 'html.parser')
        
        # tracking progress
        print(str(id_list.index(id)) + "/" + str(len(id_list)))
        print("id: {i}".format(i = id))
        
        # parse the soup and add it to the list
        card_dict = parse_card_info(temp_soup)
        card_dicts.append(card_dict)

        # Output to keep me from wondering if everything is working correctly
        for key in card_dict:
            value = card_dict[key]
            print("{k}: {v}".format(k = key, v = value))
        print("\n")

    # Convert the dictionaries in card_dicts to json and write to json file
    with open("uvs_card_data.json", "w") as json_file:
        json.dump(card_dicts, json_file)

    json_file.close()






if __name__ == "__main__":
    
    update_ids_file()

    id_list = get_ids()
    #parse_card_w_id(1250)

    execute_scrape(id_list, session)
