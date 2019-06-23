import pickle
import os
from gensim import models
from multiprocessing import Pool as P
import multiprocessing
import time
import datetime
from math import floor
from tqdm import tqdm

# setting directories
data_dir = '../master_thesis_data/weibo_deduplicated'
dates_name, texts_name = 'weibo_all_dates.pickle', 'weibo_all_texts_new.pickle'

# loading in data
with open(os.path.join(data_dir, texts_name), 'rb') as handle:
	texts = pickle.load(handle)
with open(os.path.join(data_dir, dates_name), 'rb') as handle:
	dates = pickle.load(handle)

cores = multiprocessing.cpu_count() - 2

begin_date = '2016-4-17'
begin_date = datetime.datetime.strptime(begin_date, '%Y-%m-%d')
window_size = int(356/12*6)
slider_step = int(356/12*3)
d_upper_limit = datetime.datetime.strptime('2019-4-17', '%Y-%m-%d')

n_iter = floor(((d_upper_limit - begin_date).days - slider_step)/slider_step) + 1

begin = time.time()

# placeholder for the top n keywords
li_top_n = []
  
# iterate through for continous execution
for i in range(n_iter):
	print('iter {}'.format(i))
	# determining the sub period limits
	sub_begin_date = begin_date + datetime.timedelta(days = i * slider_step)
	#print('begin date is {}'.format(sub_begin_date))
	sub_end_date = sub_begin_date + datetime.timedelta(days = window_size)
	#print('end date is {}'.format(sub_end_date))

	# getting the corresponding texts based on date range
	sub_texts = [text for i, text in enumerate(texts) if sub_begin_date <= dates[i] <= sub_end_date]

	# initiate the model
	model = models.Word2Vec(min_count=3,
		window = 10,
		size = 3000,
		sample = 6e-5,
		alpha = 0.03,
		min_alpha = 0.0007,
		negative = 80,
		workers = cores)

	# build vocab
	model.build_vocab(sub_texts)
	# train
	model.train(sub_texts, total_examples=model.corpus_count, epochs=30, report_delay=1)
	# getting the top keywords
	top_n = model.wv.most_similar(positive = ['人工智能'], topn = 50)
	li_top_n.append(top_n)
	# get time lapsed
	time_lapsed = time.time() - begin
	print('iteration {} complete, time lapsed: {}'.format(i, round(time_lapsed/60, 2)))
	print('time remaining is estimated to be {}'.format(round(((n_iter - i - 1)*time_lapsed/(i + 1))/60), 2))

# saving
with open(os.path.join(data_dir, 'top_n_list.pickle'), 'wb') as handle:
	pickle.dump(li_top_n, handle)
