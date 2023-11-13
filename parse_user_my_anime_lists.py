import os
from dotenv import load_dotenv
import requests
import xml.etree.ElementTree as ET

load_dotenv()

BASE_URL = "https://api.myanimelist.net/v2/anime/"
FIELDS = "start_date,mean,popularity,genres,num_episodes,studios"
HEADERS = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}


# get the data from the xml file
def get_data_from_xml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# parse the xml data to get the user shows
def parse_xml(xml_data):
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Create a list to store user shows
    user_shows = []

    # Iterate through each 'anime' element
    count = 10
    for anime_elem in root.findall(".//anime"):
        show_info = {
            "animedb_id": int(anime_elem.find("series_animedb_id").text),
            "title": anime_elem.find("series_title").text.strip('"'),
            "my_score": int(anime_elem.find("my_score").text),
            "series_type": anime_elem.find("series_type").text.lower(),
        }
        user_shows.append(show_info)
        count += 1

        if count == 10:
            break

    return user_shows


# augment with api data
def add_features_to_user_shows(user_shows):
    for show in user_shows:
        id = show["animedb_id"]
        url = BASE_URL + str(id) + "?fields=" + FIELDS
        response = requests.request("GET", url, headers=HEADERS)
        data = response.json()

        show["airing_date"] = data["start_date"]
        show["mean_rating"] = data["mean"]
        show["popularity_rank"] = data["popularity"]
        show["genre"] = data["genres"][0]["name"]
        show["num_episodes"] = data["num_episodes"]
        show["studio"] = data["studios"][0]["name"]

    return user_shows


def parse_user_my_anime_lists(file_path):
    xml_data = get_data_from_xml(file_path)
    user_shows = parse_xml(xml_data)
    user_shows = add_features_to_user_shows(user_shows)

    return user_shows
