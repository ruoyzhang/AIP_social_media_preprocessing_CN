import os
import datetime
from tqdm import tqdm
from multiprocessing import pool as P
import pickle
import random
import datetime

class load_and_deduplicate():
	"""
	a deduplication class designed to handle weibo social media data (text)
	it's capable of loading multiple files into one single data file as well as performing deduplication
	-------------------------------------------------------------------
	|	the current plan is to include a naïve deduplication method:  |
	|		if A == B:												  |
	|			if date(A) <= date (B):								  |
	|				del 											  |
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

		self.data_dir = data_dir

		# getting all file dirs
		self.all_file_dirs = os.listdir(data_dir)

		# placeholders for text and date data
		self.current_texts = []
		self.current_dates = []

		# placeholders for cumulative texts and dates
		self.texts = []
		self.date = []

#---------------------------------------------------------------------------------------------------------------------

	def get_file_names(self, begin_date, end_date):
		"""
		extracting data file names who fall in the range indicated by and including the begin and end dates
		begin_date & end_date: the target date range for which the data is loaded
							   have to be of the form: 'YYYY-MM-DD'
		"""

		# converting input dates into datetime format
		begin_date = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
		end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')


		# quering the data files
		# converting file names to useful info
		begin_dates = [datetime.datetime.strptime(name.split('_')[1]) for name in self.all_file_dirs]
		end_dates = [datetime.datetime.strptime(name.split('_')[2]) for name in self.all_file_dirs]

		# extracting relevant indices
		begin_indices = [i for i, date in begin_dates if date >= begin_date]
		end_indices = [i for i, date in begin_dates if date <= begin_date]

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

		# splitting files into texts and dates
		text_names = [name for name in file_names if name.split('_')[-1:] == 'texts']
		date_names = [name for name in file_names if name.split('_')[-1:] == 'dates']

		# loading in the sample date's text and dates
		for i in range(len(text_names)):

			with open(os.path.join(self.data_dir, name), 'rb') as handle:
				texts = pickle.load(handle)
			self.current_texts += texts

			with open(os.path.join(self.data_dir, sorted(all_dates)[0]), 'rb') as handle:
				dates = pickle.load(handle)
			self.current_dates += dates

#---------------------------------------------------------------------------------------------------------------------

	def naive_deduplication(self, begin_date, end_date, window_size):
		"""
		
		"""


