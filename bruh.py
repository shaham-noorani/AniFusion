import pandas as pd
import json
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_embedding(text):
    """Generate embedding for a given text using BERT."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings."""
    return cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]

def extract_genres(genres_json):
    """Extract and format genres from JSON string."""
    genres = [genre['name'] for genre in json.loads(genres_json.replace("'", "\""))]
    return ' '.join(genres)

with open('data/RyansAnimeList.json', 'r') as file:
    kethans_anime_list = json.load(file)

# Load the top 500 anime data
top_500_anime_path = 'data/top_500_anime.csv'
top_500_anime_df = pd.read_csv(top_500_anime_path)

# Process genres and generate embeddings
top_500_anime_df['Genres'] = top_500_anime_df['Genres'].apply(extract_genres)
top_500_anime_df['Embedding'] = top_500_anime_df.apply(lambda x: get_bert_embedding(x['Title'] + " " + x['Genres']), axis=1)

# Assuming each entry in kethans_anime_list represents a watched anime
# and assuming that 'get_bert_embedding' function is already defined

watched_anime_data = []
for anime in kethans_anime_list:
    if anime['my_score'] > 0:  # Assuming anime with a score greater than 0 are watched
        anime_title = anime['title']
        anime_genre = anime['genre']
        anime_rating = anime['my_score']  # User's rating for the anime
        
        # Generate embeddings for titles and genres
        embedding = get_bert_embedding(anime_title + " " + anime_genre)
        
        # Create a dictionary for each watched anime including title, genre, rating, and embedding
        watched_anime_data.append({
            'Title': anime_title,
            'Genres': anime_genre,
            'Rating': anime_rating,
            'Embedding': embedding
        })

# Create the user profile by considering embeddings, ratings, and potentially other factors
user_embeddings = np.array([anime['Embedding'] for anime in watched_anime_data])
user_ratings = np.array([anime['Rating'] for anime in watched_anime_data])

# Calculate a weighted average of embeddings based on ratings (and other factors if needed)
user_profile = np.average(user_embeddings, axis=0, weights=user_ratings)

# Compute similarity scores considering multiple factors
def calculate_similarity(row):
    anime_embedding = row['Embedding']
    similarity_embedding = compute_similarity(user_profile, anime_embedding)
    similarity_rating = row['Mean Score']  # You can add more factors here
    # Combine similarity scores with different weights as needed
    combined_similarity = 0.7 * similarity_embedding + 0.3 * similarity_rating  # Adjust weights as needed
    return combined_similarity

# Calculate similarity scores
top_500_anime_df['Similarity'] = top_500_anime_df.apply(calculate_similarity, axis=1)

watched_titles = set(anime['Title'] for anime in watched_anime_data)

# Filter out watched animes from the top 500 list
unwatched_top_anime = top_500_anime_df[~top_500_anime_df['Title'].isin(watched_titles)]

# Filter and generate recommendations (assuming watched_titles is defined)
sorted_recommendations = unwatched_top_anime.sort_values(by='Similarity', ascending=False)

# Display top 5 recommendations
final_recommendations = sorted_recommendations.head(5)[['Title', 'Similarity']]
print(final_recommendations)
