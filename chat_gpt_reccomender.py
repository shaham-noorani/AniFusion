import openai
import csv
import os

from dotenv import load_dotenv

load_dotenv()


def chatgpt_reccomendation(reccomendation_set):
    # Load the top 500 anime from the CSV file
    top_anime_names_genres = []
    top_anime_scores = {}
    with open("data/top_500_anime.csv", "r") as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            top_anime_names_genres.append(f"{row[0]} - {row[2]}/{row[3]}")
            top_anime_scores[row[0]] = row[1]

    # Use the Chat GPT API to generate recommendations based on the input anime
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        "I'm going to give you a list of the top anime on MyAnimeList right now.",
        top_anime_names_genres.__str__(),
        f'Please reccomend me up to 15 anime (just the names) that are very similar to {", ".join(reccomendation_set)}.',
        "Please only reccomend anime from list of top anime I provided and format the output as a comma seperated list.",
    ]

    prompt = []
    for message in messages:
        prompt.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=prompt,
        temperature=0,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    # parse the response and trim whitespace
    recommendations = response.choices[0].message.content.split(",")
    recommendations = [r.strip() for r in recommendations]

    # sort recomedations by score and get the top 5
    recommendations.sort(key=lambda x: top_anime_scores[x], reverse=True)
    print(recommendations[:5])

    return recommendations[:5]


chatgpt_reccomendation(
    [
        "Naruto - Action/Adventure",
        "One Punch Man - Action/Comedy",
    ]
)
