import mysql.connector
from mysql.connector import Error
from getpass import getpass
import uvs_scrape
import json

'''
def write_json():
    # Convert the dictionaries in card_dicts to json and write to json file
    with open("uvs_card_data.json", "w") as json_file:
        json.dump(card_dicts, json_file)

    json_file.close()
'''

def connect_to_mysql():
    print("Enter MySQL root password:")
    pw = getpass()

    try:
        connection = mysql.connector.connect(host='127.0.0.1',
                                            database='carddata',
                                            user='root',
                                            password=pw)

        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        print("Error while connecting to MySQL", e)

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



if __name__ == "__main___":

    id_list = uvs_scrape.get_ids()
    uvs_card_dicts = uvs_scrape.execute_scrape(id_list)

    """INSERT INTO users (first_name, last_name, email, password, location, dept,  is_admin, register_date) 
    values ('Fred', 'Smith', 'fred@gmail.com', '123456', 'New York', 'design', 0, now()),
    ('Sara', 'Watson', 'sara@gmail.com', '123456', 'New York', 'design', 0, now()),
    ('Will', 'Jackson', 'will@yahoo.com', '123456', 'Rhode Island', 'development', 1, now()),
    ('Paula', 'Johnson', 'paula@yahoo.com', '123456', 'Massachusetts', 'sales', 0, now()),
    ('Tom', 'Spears', 'tom@yahoo.com', '123456', 'Massachusetts', 'sales', 0, now());"""