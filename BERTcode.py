import json
import numpy as np
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from parse_user_my_anime_lists import get_data_from_xml, parse_xml,add_features_to_user_shows

# Initialize BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_embedding(text):
    """Generate embedding for a given text using BERT."""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

def normalize_value(value, max_value):
    """Normalize the value to a range between 0 and 1."""
    return value / max_value if max_value else 0

Username='Maharshi'

animedata=get_data_from_xml(f'data/{Username}sAnimeList.xml')

anime_List=parse_xml(animedata)

finalFeatureList=add_features_to_user_shows(anime_List)

def Create_Json_forBERT(user_shows, user_name):
    with open(f"data/{user_name}sBERTData.json", "w") as f:
        json.dump(user_shows, f)

Create_Json_forBERT(finalFeatureList,Username)

# Load user's anime list
with open(f'data/{Username}sBERTData.json', 'r') as file:
    user_anime_list = json.load(file)

# Load top 500 anime data
top_500_anime_df = pd.read_csv('data/top_500_anime.csv')

# Prepare the list of all studios (for encoding)
all_studios = set(studio for anime in user_anime_list for studio in anime['studio'])

# Normalization constants
max_user_score = 10  # Assuming the user score is out of 10
max_num_episodes = 30  # Assuming a maximum number of episodes

# Generate embeddings and additional features
watched_anime_data = []
total_scores = 0  # To keep track of the sum of scores for weighted average
for anime in user_anime_list:
    if anime['my_score'] > 0:
        content_embedding = get_bert_embedding(anime['title'] + " " + anime['genre'])
        score_norm = anime['my_score']
        episodes_norm = normalize_value(anime['num_episodes'], max_num_episodes)
        studio_embedding = get_bert_embedding(anime['studio'])
        
        augmented_embedding = np.concatenate((content_embedding.flatten(), [score_norm, episodes_norm], studio_embedding.flatten()))
        weighted_embedding = augmented_embedding * score_norm
        watched_anime_data.append(weighted_embedding)
        total_scores += score_norm

# Create user profile embedding as a weighted average
user_profile_embedding = np.sum(watched_anime_data, axis=0) / total_scores if total_scores > 0 else np.zeros_like(watched_anime_data[0])


# Process top 500 anime data and generate embeddings
# Assuming the dimensions of BERT embeddings, score, episodes, and studio embeddings are known
bert_embedding_dim = 768  # Example dimension of BERT embeddings
score_dim = 1
episodes_dim = 1
studio_embedding_dim = 768  # This should match the actual dimension

# Correct the augmented embedding generation
def create_augmented_embedding(title, genre, score, episodes, studio):
    content_embedding = get_bert_embedding(title + " " + genre).flatten()
    score_norm = [normalize_value(score, max_user_score)]
    episodes_norm = [normalize_value(episodes, max_num_episodes)]
    studio_embedding = get_bert_embedding(studio).flatten()

    # Ensure the total length matches the expected dimensions
    total_length = bert_embedding_dim + score_dim + episodes_dim + studio_embedding_dim
    augmented_embedding = np.zeros(total_length)
    
    # Populate the augmented embedding
    augmented_embedding[:bert_embedding_dim] = content_embedding
    augmented_embedding[bert_embedding_dim:bert_embedding_dim + score_dim] = score_norm
    augmented_embedding[bert_embedding_dim + score_dim:bert_embedding_dim + score_dim + episodes_dim] = episodes_norm
    augmented_embedding[-studio_embedding_dim:] = studio_embedding

    return augmented_embedding

# Update watched_anime_data and user_profile_embedding calculation
watched_anime_data = [create_augmented_embedding(anime['title'], anime['genre'], anime['my_score'], anime['num_episodes'], anime['studio']) for anime in user_anime_list if anime['my_score'] > 0]
user_profile_embedding = np.average(watched_anime_data, axis=0)

# Update process_anime_row for top 500 anime data
def process_anime_row(row):
    return create_augmented_embedding(row['Title'], row['Genres'], 0, row['Number of Episodes'], row['Studios'])

top_500_anime_df['AugmentedEmbedding'] = top_500_anime_df.apply(process_anime_row, axis=1)


# Calculate similarity between user profile and each anime in top 500
def calculate_similarity(anime_embedding):
    return cosine_similarity(anime_embedding.reshape(1, -1), user_profile_embedding.reshape(1, -1))[0][0]


# Detailed similarity calculation for each anime
top_500_anime_df['Similarity'] = top_500_anime_df['AugmentedEmbedding'].apply(calculate_similarity)

# Filter out animes already watched
watched_titles = set(anime['title'] for anime in user_anime_list)
unwatched_anime_df = top_500_anime_df[~top_500_anime_df['Title'].isin(watched_titles)]

# Recommend top 5 animes
recommendations = unwatched_anime_df.sort_values(by='Similarity', ascending=False).head(5)
print(recommendations[['Title', 'Similarity']])
