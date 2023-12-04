# AniFusion

## Setup

Install the python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

## How it works

1. It pulls the top 500 anime from MyAnimeList API
2. The user can select to either cross-reccomend anime with a partner or by themselves
3. If the user is cross-reccomending, both of their anime lists are pulled from the MyAnimeList API
   1. A similarity matrix is generated from the two lists
   2. The top 5 most similar anime are pulled from the matrix for both users
   3. These results are given to GPT-3.5, where it will augment the list with a few more reccomendations from the top 500 anime (making sure to not reccomend anything that is already on the list)
   4. These anime are then reccomended to the user, where they can know discuss the anime and help each other decide what to watch
4. If the user is looking for reccomendations for themselves
   1. A BERT embedding is made to represent the user's anime list
   2. A similarity matrix is generated from the user's list and the top 500 anime
   3. The top 5 most similar anime are pulled from the matrix

## Technologies/Tools used

- Python
- OpenAI GPT-3.5-turbo and GPT-4
- sk-learn
- transformers (BERT)
- MyAnimeList API
