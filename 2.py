#!/usr/bin/python3 -W ignore
import pandas as pd
import numpy as np
from ast import literal_eval

print("Reading the database...")

# Read metadata
md = pd.read_csv('movies_metadata_small.csv', low_memory=False)

## Function which will be used to weight the score according
## to the number of votes

def weighted_rating(x):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m95) * R) + (m95/(m95+v) * mean_vote)
#####

# Parse genres
md['genres'] = md['genres'].fillna('[]').apply(literal_eval)\
.apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

s = md.apply(lambda x: pd.Series(x['genres']),axis=1).stack()\
.reset_index(level=1, drop=True)
s.name = 'genre'
md = md.drop('genres', axis=1).join(s)

# Parse year
md['year'] = pd.to_datetime(md['release_date'], errors='coerce')\
.apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

# Clean vote counts and find mean and quantile for weighted_rating
vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
mean_vote = vote_averages.mean()
m95 = vote_counts.quantile(0.95)

# Make a leaner table
clean_md = md[['title', 'year', 'vote_count', 'vote_average', 'popularity', 'genre']]

# Add weighted rating
clean_md['wr'] = clean_md.apply(weighted_rating, axis=1)

# Sort by weighted_rating
clean_md = clean_md.sort_values('wr', ascending=False)
clean_md.to_csv(r'tmp.csv')

## UI/UX part :)
theGenre = "Comedy"
while theGenre != "Q":
    top_genres = ["Comedy", "Drama", "Documentary", "Action", "Horror"]
    print("Popular genres are: "+', '.join(top_genres))
    theGenre = input(\
    "Enter the genre on which you want to get reccomendation (Q to quit): ")
    theGenre = theGenre.capitalize()
    flag = (theGenre in top_genres)
    if flag:
        res_df = clean_md[clean_md['genre'] == theGenre]
        ## Add one random movie for a bonus
        res_df = res_df[['year', 'title']]
        rand_movie = res_df.sample(n=1)
        res_df = res_df.head(5) ## top 5 with the highest weighted_rating
        res_df = res_df.append(rand_movie)
        ## shuffle so the results are less boring
        res_df = res_df.sample(frac=1).reset_index(drop=True)
        print("You might enjoy the following movies:")
        print(res_df.to_string(index=False))
