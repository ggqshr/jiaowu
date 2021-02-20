"""
使用分词和词性标注工具将句子处理并存储到mongodb当中,写入到pos_words中
"""
from tqdm import tqdm
import re
import sys
sys.path.append("..")
from prepare.config import db,r_client
from pathlib import Path
from io import StringIO
from tempfile import NamedTemporaryFile
import pickle
from ltp import LTP

ltp = LTP(path="/home/songwenyu/data/base.tgz")

cut_word_pos_col = db.get_collection("pos_words")

def get_line():
    with r_client.pipeline(transaction=False) as p:
        while p.llen("lines").execute() != 0:
            yield p.lpop("lines").execute()[0]
lines = get_line()

teacher_info = db.get_collection("JSXXB")
all_teacher_name = [i.get("xm") for i in teacher_info.find({},{"xm":True,"_id":False}) if len(bytes(i.get("xm")[0],"utf-8")) != 1] # 只取中文的老师
all_teacher_name = [re.sub(r"([\(（].*?[\)）]|\s)","",i) for i in all_teacher_name]
all_first_name = [i[0] for i in all_teacher_name]
all_first_name = set(filter(lambda x:not ('a' <= x <= 'z'),map(lambda x:x.lower(),all_first_name)))

all_first_name_to_sub_reg = "(%s)老师" % "|".join(all_first_name)
temp_string_file = StringIO()
temp_string_file.write("感谢\n谢谢\n")
for first in all_first_name:
    temp_string_file.write("%s老师\n" % (first))
with open("../data/idiom.pth","rb") as f:
    idiom_data = pickle.load(f)
for ii in idiom_data:
    temp_string_file.write("%s\n" % (ii))
with NamedTemporaryFile(mode="w+") as f:
    f.write(temp_string_file.getvalue())
    f.flush()
    f.seek(0)
    ltp.init_dict(path=f.name,max_window=4)

def cut_func(sent_list):
    seg,hidden = ltp.seg(sent_list)
    pos = ltp.pos(hidden)
    dep = ltp.dep(hidden)
    sdp = ltp.sdp(hidden)
    for s,p,d,ss in zip(seg,pos,dep,sdp):
        yield zip(s,p),d,ss
process_list = []

def sub_match(item):
    """
    将 李老师 这种词语替换成 老师 
    """
    k,v = item
    if re.match(all_first_name_to_sub_reg,k):
        return "老师",v
    return k,v

def process(res,ll):
    insert_list = []
    for rr,sent in zip(res,ll):
        pos_res = rr[0]
        dep_res = rr[1]
        sdp_res = rr[2]
        this_item = {}
        this_item['sent'] = sent
        this_item['origin_pos'] = [(k.replace(".","").replace("$",""),v) for k,v in pos_res] # 原始的分词词性标注结果，包含标点符号
        temp_dict = [(k.replace(".","").replace("$",""),v) for k,v in pos_res if v!="wp"] 
        # temp_dict = list(map(sub_match,temp_dict))
        this_item['filter_pos'] = temp_dict # 去除标点符号的标注结果
        this_item['all_words_origin'] = [k for k,v in this_item['origin_pos']] # 原始的词语序列
        this_item['all_words_filter'] = [k for k,v in temp_dict if v != "wp"] # 过滤掉标点符号
        this_item["dep"] = dep_res
        this_item['sdp'] = sdp_res
        insert_list.append(this_item)
    return insert_list


for line in tqdm(lines):
    if len(process_list) % 100 == 0 and len(process_list) != 0:
        res = cut_func(process_list)
        insert_list = process(res,process_list)
        cut_word_pos_col.insert_many(insert_list)
        process_list.clear()
    this_line = line.strip()
    this_line = re.sub("\s+", "", this_line)
    if len(this_line) == 0:
        continue
    process_list.append(line)

if len(process_list) != 0:
    res = cut_func(process_list)
    insert_list = process(res,process_list)
    cut_word_pos_col.insert_many(insert_list)
    process_list.clear()

