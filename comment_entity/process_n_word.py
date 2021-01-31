"""
将词性为n开头的词语拿出来，做处理，
1.使用词频过滤，过滤掉词频小的词语
2.使用pmi计算
"""
import sys
sys.path.append("..")
from prepare.config import db,r_client
from collections import Counter

pos = db.get_collection("pos_words")

all_items = pos.find({},{"words_pos":True})

n_words = list()
for item in all_items:
    content = item.get("words_pos")
    for k,v in content.items():
        if v.startswith("n"):
            n_words.append(k)

cc = Counter(n_words)

all_common = cc.most_common()
all_filter_res = list(filter(lambda x:x[1]>=100,all_common))
