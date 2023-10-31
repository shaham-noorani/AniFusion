import openai
import csv
import os

from dotenv import load_dotenv

load_dotenv()


def chatgpt_reccomendation(reccomendation_set):
    # Load the top 500 anime from the CSV file
    top_anime = []
    with open("data/top_500_anime.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            top_anime.append(row[0])

    # Use the Chat GPT API to generate recommendations based on the input anime
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Recommend me some anime similar to {', '.join(reccomendation_set)}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=60,
        n=10,
        stop=None,
        temperature=0.5,
    )
    recommendations = [choice.text.strip() for choice in response.choices]

    # Filter the top 500 anime to remove any that are already in the input list
    remaining_anime = [anime for anime in top_anime if anime not in reccomendation_set]

    # Sort the remaining anime by their recommendation score
    scored_anime = []
    for anime in remaining_anime:
        score = 0
        for recommendation in recommendations:
            if anime in recommendation:
                score += 1
        scored_anime.append((anime, score))
    scored_anime.sort(key=lambda x: x[1], reverse=True)

    # Return the top 10 anime as recommendations
    top_recommendations = [anime[0] for anime in scored_anime[:10]]
    print(top_recommendations)
