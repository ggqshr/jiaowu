"""
训练lda模型
"""
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora,models
from gensim.models import LdaModel
from pickle import loads
from pathlib import Path
import numpy
numpy.random.seed(1024) # setting random seed to get the same results each time.

data_path = Path("../data/lda")
word_file = data_path.joinpath("filter_words.pth")
all_words = loads(word_file.read_bytes())
model_path = data_path.joinpath("model")
model_path.mkdir(exist_ok=True)

dic = corpora.Dictionary(all_words)
dic.filter_extremes(no_below=5,no_above=0.7)
corpus = [dic.doc2bow(text) for text in all_words]
temp = dic[0]

model = LdaModel(
    corpus=corpus,
    id2word=dic.id2token,
    chunksize=2000,
    passes=2,
    alpha='auto',
    eta='auto',
    iterations=200,
    num_topics=20,
    eval_every=1
)
model.save(str(model_path.joinpath("ldamodel.model")))