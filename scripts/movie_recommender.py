import codecs 
from math import sqrt

class movie_recommender:
	def __init__(self, data):
		# initialize movie_recommender
		self.username_to_id = {}
		self.user_id_to_name = {}
		self.movie_id_to_title = {}

		# variables set in slope one algo implementation
		self.frequencies = {}
		self.deviations = {}

		# if the dataset is a dictionary set its data to it
		if type(data).__name__ == 'dict':
			self.data = data

	# when the method is passed a movie id, converts it into the title
	def transform_movie_id_to_title(self, id):
		# check if said id exists and return the movie title, otherwise just the id
		if id in self.movie_id_to_title:
			return self.movie_id_to_title[id]
		else:
			return id

	def user_ratings(self, id, n):
		# Return n top ratings for the userid (passed as the arg)
		print ("Ratings for " + self.user_id_to_name[id])
		ratings = self.data[id]
		print(len(ratings))
		ratings = list(ratings.items())[:n]
		ratings = [(self.transform_movie_id_to_title(k), v)
                for (k, v) in ratings]
		# sort and return
		ratings.sort(key=lambda movie_tuple: movie_tuple[1], reverse = True)      
		for rating in ratings:
			print("%s\t%i" % (rating[0], rating[1]))

	def top_user_ratings(self, user, n):
		# display top n items to the user
		rated_movies = list(self.data[user].items())
		rated_movies.sort(key=lambda item_tuple: item_tuple[1], reverse=True)
		for i in range(n):
			print("%s\t%i" % (self.transform_movie_id_to_title(rated_movies[i][0]), rated_movies[i][1]))
            
	def load_movie_lens(self, path=''):
		# load ratings into self.data in the recommender class section
		self.data = {}
		
		# load the ratings file (with ascii encoding type for non-english movie titles)
		f = codecs.open(path + "ratings_p.csv", 'r', 'ascii')

		# split the ratings file into fields with values
		for line in f:
			# denominator to split by
			fields = line.split(',')
			# user id
			userid = fields[0]
			# movie id
			movie = fields[1]
			# rating number
			rating = float(fields[2].strip().strip('"'))
			# assign field metadata to recommender class variables
			if userid in self.data:
				current_ratings = self.data[userid]
			else:
				current_ratings = {}
			current_ratings[movie] = rating
			self.data[userid] = current_ratings
			self.user_id_to_name[userid] = line
			self.username_to_id[line] = userid
		f.close()

		# load movies file 
		f = codecs.open(path + "movies_tidy.csv", 'r', 'iso8859-1', 'ignore')
		# split movies file into fields with values
		for line in f:
			# denominator to split by
			fields = line.split(',')
			# movie id
			movie_id = fields[0].strip()
			# movie title
			title = fields[1].strip()
			# load movie name into the recommender class variable
			self.movie_id_to_title[movie_id] = title
		f.close()

	def compute_deviations(self):
		# go through the data set and retrieve each user's ratings
		for ratings in self.data.values():
		# loop through every item1 & rating1 in that set of ratings
			for (item, rating) in ratings.items():
				self.frequencies.setdefault(item, {})
				self.deviations.setdefault(item, {})                    
				# loop through every item2 & rating2 in that set of ratings:
				for (item2, rating2) in ratings.items():
					if item != item2:
						# as long as it is not the same item, add the difference between the ratings
						# to the computation
						self.frequencies[item].setdefault(item2, 0)
						self.deviations[item].setdefault(item2, 0.0)
						self.frequencies[item][item2] += 1
						self.deviations[item][item2] += rating - rating2
		for (item, ratings) in self.deviations.items():
			for item2 in ratings:
				ratings[item2] /= self.frequencies[item][item2]

	def slope_one_recommendations(self, user_ratings, num_recommends):
		# initialise recommendations and frequencies
		recommendations = {}
		frequencies = {}
		# for every item and rating in the user's recommendations
		for (user_item, user_rating) in user_ratings.items():
		# for every item in our dataset that the user didn't rate
			for (diff_item, diff_ratings) in self.deviations.items():
				if diff_item not in user_ratings and \
					user_item in self.deviations[diff_item]:
					freq = self.frequencies[diff_item][user_item]
					recommendations.setdefault(diff_item, 0.0)
					frequencies.setdefault(diff_item, 0)
					# add to the running sum representing the numerator
					# of the formula
					recommendations[diff_item] += (diff_ratings[user_item] + user_rating) * freq
					# keep a running sum of the frequency of diff_item
					frequencies[diff_item] += freq
		recommendations =  [(self.transform_movie_id_to_title(k),
                           v / frequencies[k])
                          for (k, v) in recommendations.items()]
		# finally sort and return
		recommendations.sort(key=lambda movie_tuple: movie_tuple[1],
                           reverse = True)
		# return the first recommendations (based on the number user input)
		return recommendations[:num_recommends]
	
# initialise the movie_recommender class
recommend=movie_recommender(0)
# load the datasets from the correct path
recommend.load_movie_lens('../data/')
# retrieving user input to record user id
user_id = input('Which user would you like to get recommendations for? ')
# printing top 10 current ratings for that user
print('Current Top Ratings by user ', user_id,':\n')
print(recommend.top_user_ratings(user_id, 10))
# retrieving user input to record the no of recommendations to be made
num_recommends = input('How many films would you like to view? \n')
# calculate deviations between movies based on the slope one algo
recommend.compute_deviations()
# print out the recommendation list
print('Movie recommendations for user ', user_id,': \n')
# USER ID FOR RECOMMENDATIONS
print(recommend.slope_one_recommendations(recommend.data[user_id],int(num_recommends)))
			