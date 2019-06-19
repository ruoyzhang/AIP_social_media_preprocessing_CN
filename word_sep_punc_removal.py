import jieba
import pickle
import os
import re
from tqdm import tqdm


# setting directories
data_dir = '../master_thesis_data/weibo_deduplicated'
dates_name, texts_name = os.listdir(data_dir)

# loading in text data only
with open(os.path.join(data_dir, texts_name), 'rb') as handle:
    texts = pickle.load(handle)

# place holder for preprocessed text
texts_new = []
# word seperation for CN
for text in tqdm(texts):
	seg_list = jieba.cut(text, cut_all = False)
	line = ' '.join(seg_list)
	line = re.sub(r'\W+', ' ', line)
	texts_new.append(line.split(' '))

# save
with open(os.path.join(data_dir, 'weibo_all_texts_new.pickle'), 'wb') as handle:
	pickle.dump(texts_new, handle)