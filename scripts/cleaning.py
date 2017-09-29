import pandas as pd
# import all data sets
data_movies = pd.read_csv('original_data/movies.csv')
data_ratings = pd.read_csv('original_data/ratings.csv')
data_tags = pd.read_csv('original_data/tags.csv')

'''
	MOVIE CLEAN-UP
'''

# create a copy of the movieset without duplicate entries
movies_nodup = data_movies.drop_duplicates(subset='title')

# separate out movie titles and years 
titles = movies_nodup.title.str.extract('(?P<title>[a-zA-Z0-9\x00-\x7F|\w !,"@#\'\%^&*)(]+[\x00-\x7F]+) (?P<year>\(\d*\))')

# remove the brackets in year values
titles['year'] = titles['year'].str.strip('()')

titles['title'] = titles['title'].str.replace('"', '')

# delete the title column from movieset
del movies_nodup['title']

# split the genres column by '|' and give it each its own row (as some have more than 1)
genres = movies_nodup['genres'].str.split('|').apply(pd.Series, 1).stack()
genres.index = genres.index.droplevel(-1) # line up with dataframe's index
genres.name = 'genre' # give the Series a name
# delete genres column from movieset
del movies_nodup['genres']

# join the new titles data frame with the original movies one
movies_tidy = pd.concat([movies_nodup,titles], axis=1)
# join the genres with the movieset
movies_tidy = movies_tidy.join(genres)
movies_tidy = movies_tidy[~movies_tidy.genre.str.contains("no genres listed")]
movies_tidy = movies_tidy.set_index('movieId')
#movies_nodup.to_csv('movies_t.csv',header=False)

'''
	RATING CLEAN-UP
'''

# count ratings per movie
ratings_count = data_ratings.groupby('movieId').size()
# convert the series from above to dataframe containing movieIds and their respective rating number
df = pd.DataFrame({'movieId':ratings_count.index, 'rating_count':ratings_count.values})
# filter out movies that have less than 20 ratings
ratings_filter = df[df.rating_count > 20]
# combine the counts and original ratings set via an intersection (to filter out movies with less than 20 ratings)
ratings_per_movie = pd.merge(data_ratings, ratings_filter, how='inner', on=['movieId'])
# re-set the index
ratings_per_movie = ratings_per_movie.set_index('userId')
# delete the rating_count column from the dataframe as it's not needed anymore
del ratings_per_movie['rating_count']
ratings_per_movie['timestamp'] = pd.to_datetime(ratings_per_movie['timestamp'],unit='s')
#ratings_per_movie.to_csv('ratings_t.csv',header=False)

'''
	TAG CLEAN-UP
'''

del data_movies['year']
del data_movies['title']
data_movies = data_movies.set_index('movieId')
data_movies.to_csv('movie_genres.csv')

tags_filtered = data_tags[~(data_tags["tag"].str.len() > 15)] # filter out tags longer than 15 character
tags_filtered = tags_filtered[~tags_filtered.tag.str.contains("ei muista")]
tags_filtered = tags_filtered[~tags_filtered.tag.str.contains("Ei muista")]
tags_filtered = tags_filtered[~tags_filtered.tag.str.contains("toplist")]
tags_filtered = tags_filtered[~tags_filtered.tag.str.contains("holes")]
tags_filtered = tags_filtered.set_index('movieId')
del tags_filtered['userId']
del tags_filtered['timestamp']
tags_filtereded['timestamp'] = pd.to_datetime(tags_filtereded['timestamp'],unit='s')
#tags_filtereded.to_csv('tags_t.csv',header=False)