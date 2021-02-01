"""
将词性为n开头的词语拿出来，做处理，
1.使用词频过滤，过滤掉词频小的词语
2.使用pmi计算
"""
import sys
sys.path.append("..")
from prepare.config import db,r_client
from collections import Counter
from pathlib import Path

pos = db.get_collection("pos_words")

all_items = pos.find({},{"words_pos":True})

n_words = list()
for item in all_items:
    content = item.get("words_pos")
    for k,v in content.items():
        if v.startswith("n"):
            n_words.append(k)
            r_client.sadd("word_"+k,item.get("_id"))

cc = Counter(n_words)

all_common = cc.most_common()
all_filter_res = list(filter(lambda x:x[1]>=100,all_common))

data_path = Path("../data/comment_entity/")
data_path.mkdir(exist_ok=True)
with open(data_path.joinpath("top_100_n_words.txt"),"w") as f:
    for item in all_filter_res:
        f.write("%s,%s\n" % (item[0],item[1]))

