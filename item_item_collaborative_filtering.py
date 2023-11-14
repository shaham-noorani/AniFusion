import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity


# Combining the data into a single DataFrame for processing
def get_similarity_matrix(user_shows_1, user_shows_2):
    combined_data = user_shows_1 + user_shows_2
    anime_df = pd.DataFrame(combined_data)

    # Prepare the data by one-hot encoding the categorical features
    encoder = OneHotEncoder()
    encoded_features = encoder.fit_transform(
        anime_df[["series_type", "studio", "genre"]]
    ).toarray()

    # Add the numerical features, including 'my_score'
    numerical_features = anime_df[
        ["mean_rating", "popularity_rank", "num_episodes", "my_score"]
    ].to_numpy()

    # Concatenate all features into one matrix
    anime_features_matrix = np.concatenate(
        [encoded_features, numerical_features], axis=1
    )

    # Calculate the similarity matrix based on the features, not including 'my_score'
    similarity_matrix = cosine_similarity(anime_features_matrix[:, :-1])
    return similarity_matrix


# Function to recommend an anime to user1 based on user2's animes
def recommend_anime_to_user(user1_animes, user2_animes, similarity_matrix):
    user1_titles = [anime["title"] for anime in user1_animes]
    user1_ratings = {anime["title"]: anime["my_score"] for anime in user1_animes}

    # Dictionary to store the weighted similarity sum for each anime not watched by user 1
    weighted_scores = {}

    # Go through each anime watched by user 2
    for i, anime2 in enumerate(user2_animes):
        if anime2["title"] not in user1_titles:
            weighted_sum = 0
            normalizing_sum = 0

            # Compare with all animes watched by user 1
            for j, anime1 in enumerate(user1_animes):
                similarity = similarity_matrix[i + len(user1_animes), j]
                weighted_sum += similarity * user1_ratings[anime1["title"]]
                normalizing_sum += similarity

            if normalizing_sum > 0:
                weighted_scores[anime2["title"]] = weighted_sum / normalizing_sum

    # Now recommend the anime with the highest 5 highest weighted scores
    if weighted_scores:
        sorted_animes = sorted(
            weighted_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [anime[0] for anime in sorted_animes[:5]], sorted_animes[:5]
    else:
        return None, 0


# Get a recommendation for both users
def generate_reccomendations(user_shows_1, user_shows_2, similarity_matrix):
    user1_recommended_anime, user1_scores = recommend_anime_to_user(
        user_shows_1, user_shows_2, similarity_matrix
    )

    user2_recommended_anime, user2_scores = recommend_anime_to_user(
        user_shows_2, user_shows_1, similarity_matrix
    )

    return (
        user1_recommended_anime,
        user1_scores,
        user2_recommended_anime,
        user2_scores,
    )
