import json
from get_top_500_anime import generate_top_500_anime_csv
from parse_user_my_anime_lists import parse_user_my_anime_lists
from item_item_collaborative_filtering import (
    get_similarity_matrix,
    generate_reccomendations,
)
from chat_gpt_reccomender import chatgpt_reccomendation

import os

# check if top 500 anime csv is in data folder. If not, generate it.
if not os.path.exists("data/top_500_anime.csv"):
    print("Generating top 500 anime csv...")
    generate_top_500_anime_csv()

# parse two users' anime lists based on input (1 = Shaham, 2 = Kethan, 3 = Ryan)
user1 = input("Enter the number of the first user (1 = Shaham, 2 = Kethan, 3 = Ryan): ")
user2 = input("Enter the number of the second user: ")

# convert 1 to Shaham, 2 to Kethan, 3 to Ryan
user1 = "Shaham" if user1 == "1" else "Kethan" if user1 == "2" else "Ryan"
user2 = "Shaham" if user2 == "1" else "Kethan" if user2 == "2" else "Ryan"

# if the data isn't saved to JSON, get the data from the xml file
if not os.path.exists(f"data/{user1}sAnimeList.json"):
    user1_anime = parse_user_my_anime_lists(f"data/{user1}sAnimeList.xml", user1)
else:
    user1_anime = json.load(open(f"data/{user1}sAnimeList.json", "r"))

if not os.path.exists(f"data/{user2}sAnimeList.json"):
    user2_anime = parse_user_my_anime_lists(f"data/{user2}sAnimeList.xml", user2)
else:
    user2_anime = json.load(open(f"data/{user2}sAnimeList.json", "r"))

# temp data to save time
# user2_anime = [
#     {
#         "animedb_id": 52034,
#         "title": "Oshi no Ko",
#         "my_score": 9,
#         "series_type": "tv",
#         "airing_date": "2023-04-12",
#         "mean_rating": 8.75,
#         "popularity_rank": 281,
#         "genre": "Drama",
#         "num_episodes": 11,
#         "studio": "Doga Kobo",
#     },
#     {
#         "animedb_id": 31646,
#         "title": "3-gatsu no Lion",
#         "my_score": 0,
#         "series_type": "tv",
#         "airing_date": "2016-10-08",
#         "mean_rating": 8.38,
#         "popularity_rank": 293,
#         "genre": "Childcare",
#         "num_episodes": 22,
#         "studio": "Shaft",
#     },
#     {
#         "animedb_id": 38101,
#         "title": "5-toubun no Hanayome",
#         "my_score": 7,
#         "series_type": "tv",
#         "airing_date": "2019-01-11",
#         "mean_rating": 7.66,
#         "popularity_rank": 168,
#         "genre": "Comedy",
#         "num_episodes": 12,
#         "studio": "Tezuka Productions",
#     },
#     {
#         "animedb_id": 41457,
#         "title": "86",
#         "my_score": 0,
#         "series_type": "tv",
#         "airing_date": "2021-04-11",
#         "mean_rating": 8.29,
#         "popularity_rank": 258,
#         "genre": "Action",
#         "num_episodes": 11,
#         "studio": "A-1 Pictures",
#     },
#     {
#         "animedb_id": 11759,
#         "title": "Accel World",
#         "my_score": 8,
#         "series_type": "tv",
#         "airing_date": "2012-04-07",
#         "mean_rating": 7.22,
#         "popularity_rank": 272,
#         "genre": "Action",
#         "num_episodes": 24,
#         "studio": "Sunrise",
#     },
# ]

# user1_anime = [
#     {
#         "animedb_id": 52034,
#         "title": "Oshi no Ko",
#         "my_score": 9,
#         "series_type": "tv",
#         "airing_date": "2023-04-12",
#         "mean_rating": 8.75,
#         "popularity_rank": 281,
#         "genre": "Drama",
#         "num_episodes": 11,
#         "studio": "Doga Kobo",
#     },
#     {
#         "animedb_id": 40679,
#         "title": "2.43: Seiin Koukou Danshi Volley-bu",
#         "my_score": 0,
#         "series_type": "tv",
#         "airing_date": "2021-01-08",
#         "mean_rating": 6.14,
#         "popularity_rank": 1883,
#         "genre": "Drama",
#         "num_episodes": 12,
#         "studio": "David Production",
#     },
#     {
#         "animedb_id": 31646,
#         "title": "3-gatsu no Lion",
#         "my_score": 0,
#         "series_type": "tv",
#         "airing_date": "2016-10-08",
#         "mean_rating": 8.38,
#         "popularity_rank": 293,
#         "genre": "Childcare",
#         "num_episodes": 22,
#         "studio": "Shaft",
#     },
#     {
#         "animedb_id": 35180,
#         "title": "3-gatsu no Lion 2nd Season",
#         "my_score": 0,
#         "series_type": "tv",
#         "airing_date": "2017-10-14",
#         "mean_rating": 8.93,
#         "popularity_rank": 562,
#         "genre": "Childcare",
#         "num_episodes": 22,
#         "studio": "Shaft",
#     },
#     {
#         "animedb_id": 22199,
#         "title": "Akame ga Kill!",
#         "my_score": 4,
#         "series_type": "tv",
#         "airing_date": "2014-07-07",
#         "mean_rating": 7.47,
#         "popularity_rank": 30,
#         "genre": "Action",
#         "num_episodes": 24,
#         "studio": "White Fox",
#     },
# ]

# use item-item collaborative filtering to generate recommendations
similarity_matrix = get_similarity_matrix(user1_anime, user2_anime)

(
    user1_reccomendations,
    user1_scores,
    user2_reccomendations,
    user2_scores,
) = generate_reccomendations(user1_anime, user2_anime, similarity_matrix)

# enhance recommendations with chat gpt
user1_final_reccomendations = user1_reccomendations + chatgpt_reccomendation(
    user1_reccomendations, user1_anime
)

user2_final_reccomendations = user2_reccomendations + chatgpt_reccomendation(
    user2_reccomendations, user2_anime
)

print()
print(f"{user1}'s recommendations:\n{','.join(user1_final_reccomendations)}")
print()
print(f"{user2}'s recommendations:\n{','.join(user2_final_reccomendations)}")
