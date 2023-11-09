import os

from dotenv import load_dotenv

load_dotenv()

print(os.getenv("MAL_CLIENT_ID"))

import requests

import xml.etree.ElementTree as ET

def read_xml_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Replace 'your_xml_file.xml' with the actual file name
xml_file_path = 'data/ShahamMyAnimeList.xml'

def parse_xml(xml_data):
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Create a list to store user shows
    user_shows = []

    # Iterate through each 'anime' element
    for anime_elem in root.findall(".//anime"):
        show_info = {
            "animedb_id": int(anime_elem.find("series_animedb_id").text),
            "title": anime_elem.find("series_title").text.strip('\"'),
            "series_type": anime_elem.find("series_type").text.lower(),
            "my_score": int(anime_elem.find("my_score").text),
            "status": anime_elem.find("my_status").text.lower(),
        }
        user_shows.append(show_info)

    return user_shows

# Check if the file exists
if os.path.exists(xml_file_path):
    xml_data = read_xml_file(xml_file_path)
    user_shows_result = parse_xml(xml_data)
    print("user_shows =", user_shows_result)
else:
    print(f"The file {xml_file_path} does not exist.")


# # get the raw data from the xmls
# user_shows = [
#     {
#         animedb_id: 12124321,
#         title: "sd",
#         series_type: "tv",
#         my_score: 8,
#         status: "completed",
#     }
# ]



# augment with api data
url = "https://api.myanimelist.net/v2/anime/52034?fields=genres"
payload = {}
headers = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)

# return that data
