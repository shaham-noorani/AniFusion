import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from parse_user_my_anime_lists import add_features_to_user_shows, get_data_from_xml, parse_xml

# Create fake data for two users
xml_data_1 = get_data_from_xml("data\KethansAnimeList.xml")
xml_data_1 = parse_xml(xml_data_1)
user_shows_1 = add_features_to_user_shows(xml_data_1)

xml_data_2 = get_data_from_xml("data\ShahamMyAnimeList.xml")
xml_data_2 = parse_xml(xml_data_2)
user_shows_2 = add_features_to_user_shows(xml_data_2)

print(user_shows_1)
print(user_shows_2)

# Combining the data into a single DataFrame for processing
combined_data = user_shows_1 + user_shows_2
anime_df = pd.DataFrame(combined_data)

# Prepare the data by one-hot encoding the categorical features
encoder = OneHotEncoder()
encoded_features = encoder.fit_transform(anime_df[['series_type', 'status', 'studio', 'genres']]).toarray()

# Add the numerical features, including 'my_score'
numerical_features = anime_df[['mean_score', 'popularity_rank', 'number_of_episodes', 'my_score']].to_numpy()

# Concatenate all features into one matrix
anime_features_matrix = np.concatenate([encoded_features, numerical_features], axis=1)

# Calculate the similarity matrix based on the features, not including 'my_score'
similarity_matrix = cosine_similarity(anime_features_matrix[:, :-1])

# Function to recommend an anime to user1 based on user2's animes
def recommend_anime_to_user1(user1_animes, user2_animes, similarity_matrix):
    user1_titles = [anime['title'] for anime in user1_animes]
    user1_ratings = {anime['title']: anime['my_score'] for anime in user1_animes}
    user2_titles = [anime['title'] for anime in user2_animes]

    # Dictionary to store the weighted similarity sum for each anime not watched by user 1
    weighted_scores = {}

    # Go through each anime watched by user 2
    for i, anime2 in enumerate(user2_animes):
        if anime2['title'] not in user1_titles:  # Only consider animes not watched by user 1
            weighted_sum = 0
            normalizing_sum = 0
            # Compare with all animes watched by user 1
            for j, anime1 in enumerate(user1_animes):
                # Weight by the rating user 1 gave this anime
                similarity = similarity_matrix[i+len(user1_animes), j]
                weighted_sum += similarity * user1_ratings[anime1['title']]
                normalizing_sum += similarity
            # Avoid division by zero
            if normalizing_sum > 0:
                weighted_scores[anime2['title']] = weighted_sum / normalizing_sum

    # Now recommend the anime with the highest weighted similarity score
    if weighted_scores:
        recommended_title = max(weighted_scores, key=weighted_scores.get)
        return recommended_title, weighted_scores[recommended_title]
    else:
        return None, 0

# Get a recommendation for user1
recommended_anime, score = recommend_anime_to_user1(user_shows_1, user_shows_2, similarity_matrix)
if recommended_anime:
    print(f"Recommended Anime for User 1: {recommended_anime} with predicted score {score:.2f}")
else:
    print("No recommendation could be made.")
