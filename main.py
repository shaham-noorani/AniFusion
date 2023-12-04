import json
from get_top_500_anime import generate_top_500_anime_csv
from parse_user_my_anime_lists import parse_user_my_anime_lists
from item_item_collaborative_filtering import (
    get_similarity_matrix,
    generate_reccomendations,
)
from chat_gpt_reccomender import chatgpt_reccomendation

import os

from single_user_reccomender_bert import SingleUserAnimeRecommendation

# check if top 500 anime csv is in data folder. If not, generate it.
if not os.path.exists("data/top_500_anime.csv"):
    print("Generating top 500 anime csv...")
    generate_top_500_anime_csv()


def cross_reccomend():
    # parse two users' anime lists based on input (1 = Shaham, 2 = Kethan, 3 = Ryan, 4 = Maharshi)
    user1 = input(
        "Enter the number of the first user (1 = Shaham, 2 = Kethan, 3 = Ryan, 4 = Maharshi): "
    )
    user2 = input("Enter the number of the second user: ")

    # convert 1 to Shaham, 2 to Kethan, 3 to Ryan, 4 to Maharshi
    user1 = "Shaham" if user1 == "1" else "Kethan" if user1 == "2" else "Ryan" if user1 == "3" else "Maharshi"
    user2 = "Shaham" if user2 == "1" else "Kethan" if user2 == "2" else "Ryan" if user2 == "3" else "Maharshi"

    # if the data isn't saved to JSON, get the data from the xml file
    if not os.path.exists(f"data/{user1}sAnimeList.json"):
        user1_anime = parse_user_my_anime_lists(f"data/{user1}sAnimeList.xml", user1)
    else:
        user1_anime = json.load(open(f"data/{user1}sAnimeList.json", "r"))

    if not os.path.exists(f"data/{user2}sAnimeList.json"):
        user2_anime = parse_user_my_anime_lists(f"data/{user2}sAnimeList.xml", user2)
    else:
        user2_anime = json.load(open(f"data/{user2}sAnimeList.json", "r"))

    # use item-item collaborative filtering to generate recommendations
    similarity_matrix = get_similarity_matrix(user1_anime, user2_anime)

    (
        user1_reccomendations,
        user1_scores,
        user2_reccomendations,
        user2_scores,
    ) = generate_reccomendations(user1_anime, user2_anime, similarity_matrix)

    user1_final_reccomendations = user1_reccomendations + chatgpt_reccomendation(
        user1_reccomendations, user1_anime
    )

    user2_final_reccomendations = user2_reccomendations + chatgpt_reccomendation(
        user2_reccomendations, user2_anime
    )

    print()
    user_1_reccomendations_as_string = "\n- ".join(user1_final_reccomendations)
    print(f"{user1}'s recommendations: \n- {user_1_reccomendations_as_string}")

    print()
    user_2_reccomendations_as_string = "\n- ".join(user2_final_reccomendations)
    print(f"{user2}'s recommendations:\n- {user_2_reccomendations_as_string}")


def single_reccomend():
    user = input(
        "Enter the number of the first user (1 = Shaham, 2 = Kethan, 3 = Ryan, 4 = Maharshi): "
    )
    user = "Shaham" if user == "1" else "Kethan" if user == "2" else "Ryan" if user == "3" else "Maharshi"

    recommendation_system = SingleUserAnimeRecommendation(user)
    recommendations = recommendation_system.recommend_anime()
    print(recommendations)


# ask user if they would like to cross-reccomend or reccomend based on their own list
choice = input(
    "Would you like to cross-reccomend or reccomend based on your own list? (1 = cross-reccomend, 2 = reccomend based on your own list): "
)

if choice == "1":
    cross_reccomend()
else:
    single_reccomend()
