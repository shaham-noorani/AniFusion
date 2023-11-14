import openai
import csv
import os

from dotenv import load_dotenv

load_dotenv()


def load_top_500_anime():
    # Load the top 500 anime from the CSV file
    # Title,Rank,Mean Score,Genres,Number of Episodes,Media Type,Studios,Start Date
    top_anime_names_genres = []
    with open("data/top_500_anime.csv", "r") as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            # genres looks like this "[{'id': 1, 'name': 'Action'}, {'id': 27, 'name': 'Shounen'}, ...]"
            main_genre = (
                row[3].split(",")[0].split(":")[1].strip("'").strip("[").strip("'")
            )
            second_genre = (
                row[3].split(",")[1].split(":")[1].strip("'").strip("]").strip("'")
            )

            top_anime_names_genres.append(f"{row[0]} - {main_genre}/{second_genre}")
            # stop at 250
            if len(top_anime_names_genres) == 200:
                break

    return top_anime_names_genres


def remove_seen_anime(reccomendation_set, watched_set):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # from watched anime, onky keep the titles
    watched_set = [anime["title"] for anime in watched_set]

    messages = [
        "I'm going to give you a list of all the anime I've seen:",
        watched_set.__str__(),
        "I'm also going to give you a list of reccomendations based on the anime I've seen:",
        reccomendation_set.__str__(),
        "\nPlease remove any anime that I've seen from the list of reccomendations.",
    ]

    prompt = [
        {
            "role": "system",
            "content": "Only respond in titles of anime and as a comma seperated list.",
        }
    ]
    for message in messages:
        prompt.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=prompt,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # parse the response and trim whitespace
    recommendations = response.choices[0].message.content.split(",")
    recommendations = [r.strip().strip("'") for r in recommendations]

    return recommendations


def chatgpt_reccomendation(reccomendation_set, user_anime):
    # Load the top 500 anime from the CSV file
    top_anime_names_genres = load_top_500_anime()

    # Use the Chat GPT API to generate recommendations based on the input anime
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        "I'm going to give you a list of the top anime on MyAnimeList right now.",
        top_anime_names_genres.__str__(),
        f'Please reccomend me up to 5 anime (just the names) that are very similar to {", ".join(reccomendation_set)}.',
    ]

    prompt = [
        {
            "role": "system",
            "content": "Only respond in titles of anime and as a comma seperated list. You only know of anime that are provided by the user",
        }
    ]
    for message in messages:
        prompt.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=prompt,
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # parse the response and trim whitespace
    recommendations = response.choices[0].message.content.split(",")
    recommendations = [r.strip() for r in recommendations]

    unseen_anime = remove_seen_anime(recommendations, user_anime)
    return unseen_anime[:5]
