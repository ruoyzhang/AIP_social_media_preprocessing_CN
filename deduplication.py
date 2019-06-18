import os
import datetime
from tqdm import tqdm
from multiprocessing import pool as P
import pickle
import random
import datetime
from math import floor
from datetime import timedelta
import time

class load_and_deduplicate():
	"""
	a deduplication class designed to handle weibo social media data (text)
	it's capable of loading multiple files into one single data file as well as performing deduplication
	-------------------------------------------------------------------
	|	the current plan is to include a naïve deduplication method:  |
	|		if A == B:												  |
	|			if date(A) <= date (B):								  |
	|				del B											  |
	|			else:												  |
	|				del A 											  |
	-------------------------------------------------------------------
	future plans will see a method of LSH Min Hash being added for more sophiscated needs
	"""
#---------------------------------------------------------------------------------------------------------------------

	def __init__(self, data_folder_dir):
		"""
		the init method for the class

		data_folder_dir: the directory to where the data is saved
		"""

		self.data_dir = data_folder_dir

		# getting all file dirs
		self.all_file_dirs = [file for file in os.listdir(self.data_dir) if file[:4] == '人工智能']

		# placeholders for text and date data
		self.current_texts = []
		self.current_dates = []

		# placeholders for cumulative texts and dates
		self.texts = []
		self.dates = []

#---------------------------------------------------------------------------------------------------------------------

	def get_file_names(self, begin_date, end_date):
		"""
		extracting data file names who fall in the range indicated by and including the begin and end dates
		begin_date & end_date: the target date range for which the data is loaded
							   have to be of datetime format
		"""

		# quering the data files
		# converting file names to useful info
		begin_dates = [datetime.datetime.strptime(name.split('_')[1], '%Y-%m-%d') for name in self.all_file_dirs]
		end_dates = [datetime.datetime.strptime(name.split('_')[2], '%Y-%m-%d') for name in self.all_file_dirs]

		# extracting relevant indices
		begin_indices = [i for i, date in enumerate(begin_dates) if date >= begin_date]
		end_indices = [i for i, date in enumerate(end_dates) if date <= end_date]

		# take the intercept of the 2 lists of indices and determine the correct file names
		index_overlap = list(set(begin_indices)&set(end_indices))
		file_names = [name for i, name in enumerate(self.all_file_dirs) if i in index_overlap]

		return(file_names)

#---------------------------------------------------------------------------------------------------------------------

	def load_data(self, file_names):
		"""
		loading texts and dates into the current placeholder variables

		file_names: a list of file names to be loaded into one variable
		"""

		# loading the names without discriminating whether its date or text
		fnames = ['_'.join(name.split('_')[:3]) for name in file_names]

		# resetting current placeholders
		self.current_texts = []
		self.current_dates = []

		# loading in the sample data's text and dates
		for name in fnames:
			with open(os.path.join(self.data_dir, name + '_texts.pickle'), 'rb') as handle:
				texts = pickle.load(handle)
			self.current_texts += texts

			with open(os.path.join(self.data_dir, name + '_dates.pickle'), 'rb') as handle:
				dates = pickle.load(handle)
			self.current_dates += dates

#---------------------------------------------------------------------------------------------------------------------

	def deduplicate(self):
		"""
		function for deduplication
		"""
		# iterating for getting exact duplicates
		clusters = []
		for i, tweet_0 in enumerate(self.current_texts):
			if sum([i in clus for clus in clusters]) == 0:
				clusters.append([i])
			else:
				continue
			for j,tweet_1 in enumerate(self.current_texts[i+1:]):
				if tweet_0 == tweet_1:
					clusters[-1].append(i+j+1)

		# getting clusters that have legnth of longer than 1
		clusters = [clus for clus in clusters if len(clus) > 1]

		# iterate over the clusters to select the earliest tweet
		ind_remove = []
		for clus in clusters:
			min_date = None
			ind_holder = 0
			for i, ind in enumerate(clus):
				if i == 0:
					min_date = self.current_dates[ind]
					ind_holder = ind
				elif self.current_dates[ind] < min_date:
					min_date = self.current_dates[ind]
					ind_holder = ind
			ind_remove += [ind for ind in clus if ind != ind_holder]

		# now remove the entries indentified above
		self.texts += [text for i, text in enumerate(self.current_texts) if i not in ind_remove]
		self.dates += [date for i, date in enumerate(self.current_dates) if i not in ind_remove]

#---------------------------------------------------------------------------------------------------------------------

	def naive_deduplication(self, begin_date, end_date, window_size):
		"""
		wrapper function that streamlines the naive deduplication process
		"""

		# converting input dates into datetime format
		begin_date = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
		end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

		# calculating the total number of days
		n_days = (end_date - begin_date).days

		# calculating the number of iterations needed
		if n_days%window_size == 0:
			n_iter = int(n_days/window_size)
		else:
			n_iter = floor(n_days/window_size) + 1

		print('beginning deduplcation process')

		time_begin = time.time()
		# iterate for deduplication
		for i in range(n_iter):
			# setting sub_begin_date and sub_end_date
			sub_begin_date = begin_date + timedelta(days = i*(window_size))
			if i != n_iter:
				sub_end_date = sub_begin_date + timedelta(days = window_size - 1)
			else:
				sub_end_date = end_date

			# reading file names
			target_file_names = self.get_file_names(sub_begin_date, sub_end_date)

			# loding in the file to placeholder class vars
			self.load_data(target_file_names)

			# deduplicate
			self.deduplicate()

			# updating progress
			print('deduplication completed for iteration {}'.format(i))
			print('time lapsed so far: {}'.format(time.time() - time_begin))

#---------------------------------------------------------------------------------------------------------------------
	
	def reset_holders(self):
		self.texts = []
		self.dates = []
		self.current_texts = []
		self.current_dates = []

#---------------------------------------------------------------------------------------------------------------------

	def save_all(self, save_dir, save_name):
		"""
		function to save

		save_name: name for the files (texts and dates), without the extension
		"""
		with open(os.path.join(save_dir, save_name + '_texts.pickle'), 'wb') as handle:
			pickle.dump(self.texts, handle)

		with open(os.path.join(save_dir, save_name + '_dates.pickle'), 'wb') as handle:
			pickle.dump(self.dates, handle)

#---------------------------------------------------------------------------------------------------------------------






