import os

from dotenv import load_dotenv

load_dotenv()

print(os.getenv("MAL_CLIENT_ID"))

import requests

url = "https://api.myanimelist.net/v2/anime/52034?fields=genres"
payload = {}
headers = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)
