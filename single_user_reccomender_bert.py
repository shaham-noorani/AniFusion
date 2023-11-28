import json
import os
import numpy as np
import pandas as pd
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from parse_user_my_anime_lists import parse_user_my_anime_lists


class SingleUserAnimeRecommendation:
    def __init__(self, username):
        self.username = username
        self.max_user_score = 10
        self.max_num_episodes = 30
        self.bert_embedding_dim = 768
        self.score_dim = 1
        self.episodes_dim = 1
        self.studio_embedding_dim = 768

        # Initialize BERT tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertModel.from_pretrained("bert-base-uncased")

        if not os.path.exists(f"data/{self.username}sAnimeList.json"):
            self.user_anime_list = self.parse_user_anime_list()
        else:
            with open(f"data/{self.username}sAnimeList.json", "r") as file:
                self.user_anime_list = json.load(file)

        # Load top 500 anime data
        self.top_500_anime_df = pd.read_csv("data/top_500_anime.csv")

    def parse_user_anime_list(self):
        animedata = parse_user_my_anime_lists(
            f"data/{self.username}sAnimeList.xml", self.username
        )
        return animedata

    def get_bert_embedding(self, text):
        """Generate embedding for a given text using BERT."""
        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()

    def normalize_value(self, value, max_value):
        """Normalize the value to a range between 0 and 1."""
        return value / max_value if max_value else 0

    def create_augmented_embedding(self, title, genre, score, episodes, studio):
        content_embedding = self.get_bert_embedding(title + " " + genre).flatten()
        score_norm = [self.normalize_value(score, self.max_user_score)]
        episodes_norm = [self.normalize_value(episodes, self.max_num_episodes)]
        studio_embedding = self.get_bert_embedding(studio).flatten()

        # Ensure the total length matches the expected dimensions
        total_length = (
            self.bert_embedding_dim
            + self.score_dim
            + self.episodes_dim
            + self.studio_embedding_dim
        )
        augmented_embedding = np.zeros(total_length)

        # Populate the augmented embedding
        augmented_embedding[: self.bert_embedding_dim] = content_embedding
        augmented_embedding[
            self.bert_embedding_dim : self.bert_embedding_dim + self.score_dim
        ] = score_norm
        augmented_embedding[
            self.bert_embedding_dim
            + self.score_dim : self.bert_embedding_dim
            + self.score_dim
            + self.episodes_dim
        ] = episodes_norm
        augmented_embedding[-self.studio_embedding_dim :] = studio_embedding

        return augmented_embedding

    def generate_user_profile_embedding(self):
        watched_anime_data = []
        total_scores = 0  # To keep track of the sum of scores for weighted average

        for anime in self.user_anime_list:
            if anime["my_score"] > 0:
                augmented_embedding = self.create_augmented_embedding(
                    anime["title"],
                    anime["genre"],
                    anime["my_score"],
                    anime["num_episodes"],
                    anime["studio"],
                )
                weighted_embedding = augmented_embedding * anime["my_score"]
                watched_anime_data.append(weighted_embedding)
                total_scores += anime["my_score"]

        # Create user profile embedding as a weighted average
        self.user_profile_embedding = (
            np.sum(watched_anime_data, axis=0) / total_scores
            if total_scores > 0
            else np.zeros_like(watched_anime_data[0])
        )

    def process_top_500_anime(self):
        def process_anime_row(row):
            return self.create_augmented_embedding(
                row["Title"],
                row["Genres"],
                0,
                row["Number of Episodes"],
                row["Studios"],
            )

        self.top_500_anime_df["AugmentedEmbedding"] = self.top_500_anime_df.apply(
            process_anime_row, axis=1
        )

    def calculate_similarity(self, anime_embedding):
        return cosine_similarity(
            anime_embedding.reshape(1, -1), self.user_profile_embedding.reshape(1, -1)
        )[0][0]

    def recommend_anime(self):
        self.generate_user_profile_embedding()
        print("User anime list processed")
        self.process_top_500_anime()
        print("Top 500 anime processed")

        # Detailed similarity calculation for each anime
        self.top_500_anime_df["Similarity"] = self.top_500_anime_df[
            "AugmentedEmbedding"
        ].apply(self.calculate_similarity)
        print("Similarity calculated")

        # Filter out animes already watched
        watched_titles = set(anime["title"] for anime in self.user_anime_list)
        unwatched_anime_df = self.top_500_anime_df[
            ~self.top_500_anime_df["Title"].isin(watched_titles)
        ]
        print("Unwatched animes filtered")

        # Recommend top 5 animes
        recommendations = unwatched_anime_df.sort_values(
            by="Similarity", ascending=False
        ).head(5)
        return recommendations[["Title", "Similarity"]]


if __name__ == "__main__":
    username = "Shaham"
    recommendation_system = SingleUserAnimeRecommendation(username)
    recommendations = recommendation_system.recommend_anime()
    print(recommendations)
