"""
将词性为n开头的词语拿出来，做处理，
1.使用词频过滤，过滤掉词频小的词语
2.使用pmi计算
"""
import sys
from tqdm import tqdm
sys.path.append("..")
from prepare.config import db, r_client
from pathlib import Path
from collections import Counter


def get_words_wirte_to_redis():
    pos = db.get_collection("pos_words")

    all_items = pos.find({}, {"words_pos": True})

    n_words = list()
    with r_client.pipeline(transaction=False) as p:
        for item in tqdm(all_items):
            content = item.get("words_pos")
            for k, v in content.items():
                if v.startswith("n"):
                    n_words.append(k)
                    p.sadd("word:"+k, str(item.get("_id")))
    return n_words


def get_counter_ge_100(n_words):
    cc = Counter(n_words)

    all_common = cc.most_common()
    all_filter_res = list(filter(lambda x: x[1] >= 100, all_common))

    data_path = Path("../data/comment_entity/")
    data_path.mkdir(exist_ok=True)
    with open(data_path.joinpath("top_100_n_words.txt"), "w") as f:
        for item in all_filter_res:
            f.write("%s,%s\n" % (item[0], item[1]))
    return all_filter_res


def cal_pmi(w1, w2, client):
    w1_len = client.scard("word:%s" % w1)
    w2_len = client.scard("word:%s" % w2)
    w1_w2_inter = len(client.sinter("word:%s" % w1, "word:%s" % w2))
    return w1_w2_inter / (w1_len * w2_len)


def use_select_cal_pmi(words):
    res_list = []
    with r_client.pipeline(transaction=False) as p:
        for word,_ in words:
            res_list.append((word,cal_pmi("老师",word,p)))
    print(res_list)


if __name__ == '__main__':
    # n_words = get_words_wirte_to_redis()
    # filter_res = get_counter_ge_100(n_words)
    filter_res = [i.split(",") for i in filter(None,Path("../data/comment_entity/top_100_n_words.txt").read_text().split("\n"))]
    use_select_cal_pmi(filter_res)
