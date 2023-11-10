import os
from dotenv import load_dotenv
import requests
import csv

load_dotenv()

BASE_URL = "https://api.myanimelist.net/v2/anime/ranking"
LIMIT = 500
HEADERS = {"X-MAL-CLIENT-ID": os.getenv("MAL_CLIENT_ID")}
FIELDS = "title,rank,mean,genres,num_episodes,media_type,studios,start_date"

# Fetch the top 500 anime
def get_top_500_anime():
    url = f"{BASE_URL}?ranking_type=all&limit={LIMIT}&fields={FIELDS}"
    print("API Request URL:", url)
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    return data.get("data", [])


# Create and write to CSV file
def write_to_csv(anime_data, file_path="top_anime.csv"):
    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Title", "Rank", "Mean Score", "Genres", "Number of Episodes", "Media Type", "Studios", "Start Date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data
        for anime in anime_data:
            writer.writerow({
                "Title": anime["node"]["title"],
                "Rank": anime["node"]["rank"],
                "Mean Score": anime["node"]["mean"],
                "Genres": anime["node"]["genres"],
                "Number of Episodes": anime["node"]["num_episodes"],
                "Media Type": anime["node"]["media_type"],
                "Studios": anime["node"]["studios"],
                "Start Date": anime["node"]["start_date"],
            })

# Display the top 500 anime
top_500_anime = get_top_500_anime()

# Write to CSV
if top_500_anime:
    write_to_csv(top_500_anime)
    print("CSV file created successfully.")
else:
    print("No data to write to CSV.")
# # Display the top 500 anime
# top_500_anime = get_top_500_anime()
# for anime in top_500_anime:
#     print("Title:", anime["node"]["title"])

#     print("Rank:", anime["node"]["rank"])
#     print("Mean Score:", anime["node"]["mean"])
#     print("Genres:", anime["node"]["genres"])
#     print("Number of Episodes:", anime["node"]["num_episodes"])
#     print("Media Type:", anime["node"]["media_type"])
#     print("Studios:", anime["node"]["studios"])
#     print("Start Date:", anime["node"]["start_date"])
#     print("----")
