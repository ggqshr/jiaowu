import logging
import os
import gensim
import glob

from gensim.models import word2vec
from gensim.models.word2vec import PathLineSentences

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,filename="../result/training.log")


all_files = word2vec.PathLineSentences("../data/word_data") 

model = word2vec.Word2Vec(all_files,hs=1,min_count=5,iter=5, window=5,size=300,sg=1,workers=40)
model.save("../result/model_data/1.bin")
model.wv.save_word2vec_format("../result/model_data/1.dict")


# for file in file_list:
#     model = gensim.models.Word2Vec.load("../result/1.bin")
#     new_sentences = word2vec.LineSentence(file) 
#     model.build_vocab(new_sentences, update=True)
#     model.train(new_sentences,epochs=5,total_examples=model.corpus_count)
#     model.save("../result/1.bin")
#     model.wv.save_word2vec_format("../result/1.dict")

