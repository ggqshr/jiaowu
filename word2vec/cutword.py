"""
分词，将分词之后的结果存储到data/word2vec文件夹下的word_cut_res.txt当中
"""
from tqdm import tqdm
import chardet
import pandas as pd
import chardet
import jieba
import glob
import os
import re
from multiprocessing import Pool
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

target_dir = Path("../data/word2vec")
target_dir.mkdir(exist_ok=True)

# sentence seperate pattern
sent_sep_pattern = re.compile(
    '[﹒﹔﹖﹗．。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$)')  # del ：；


def sentence_split(article):
    sent_list = []
    for ele in sent_sep_pattern.split(article):
        if sent_sep_pattern.match(ele) and sent_list:
            sent_list[-1] += ele
        elif ele:
            sent_list.append(ele)
    return sent_list


def process(line):
    res = []
    line = re.sub("\s+", "", line)
    sentences = sentence_split(line)
    for sent in sentences:
        sent_words = jieba.cut(sent)
        res.append("%s%s" % (" ".join(sent_words), "\n"))
    return res


if __name__ == "__main__":
    file = Path("../data/all_text.txt")
    with file.open() as f:
        content = f.read()
        lines = list(filter(None,content.split("\n"))) 
    with open(target_dir.joinpath("word_cut_res.txt"),'w') as f:
        for line in tqdm(lines):
            f.writelines(process(line))
