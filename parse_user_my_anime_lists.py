import os

from dotenv import load_dotenv

load_dotenv()

print(os.getenv("MAL_CLIENT_ID"))

import requests

# get the raw data from the xmls
user_shows = [
    {
        animedb_id: 12124321,
        title: "sd",
        series_type: "tv",
        my_score: 8,
        status: "completed",
    }
]

# augment with api data
url = "https://api.myanimelist.net/v2/anime/52034?fields=genres"
payload = {}
headers = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)

# return that data
