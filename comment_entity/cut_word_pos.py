"""
使用分词和词性标注工具将句子处理并存储到mongodb当中,写入到pos_words中
"""
import fool
from tqdm import tqdm
import re
import sys
sys.path.append("..")
from prepare.config import db
from pathlib import Path
from io import StringIO
from tempfile import NamedTemporaryFile
import pickle

cut_word_pos_col = db.get_collection("pos_words")

data_path = Path("../data/all_text.txt")
content = data_path.read_text(encoding="utf-8")
lines = list(filter(None,map(lambda x:x.strip(),content.split("\n")))) 

teacher_info = db.get_collection("JSXXB")
all_teacher_name = [i.get("xm") for i in teacher_info.find({},{"xm":True,"_id":False}) if len(bytes(i.get("xm")[0],"utf-8")) != 1] # 只取中文的老师
all_teacher_name = [re.sub(r"([\(（].*?[\)）]|\s)","",i) for i in all_teacher_name]
all_first_name = [i[0] for i in all_teacher_name]
all_first_name = set(filter(lambda x:not ('a' <= x <= 'z'),map(lambda x:x.lower(),all_first_name)))

all_first_name_to_sub_reg = "(%s)老师" % "|".join(all_first_name)
temp_string_file = StringIO()
for first in all_first_name:
    temp_string_file.write("%s老师 %s\n" % (first,10))
with open("../data/idiom.pth","rb") as f:
    idiom_data = pickle.load(f)
for ii in idiom_data:
    temp_string_file.write("%s %s\n" % (ii,100))
with NamedTemporaryFile(mode="a") as f:
    f.write(temp_string_file.getvalue())
    f.flush()
    f.seek(0)
    fool.load_userdict(f.name)

cut_func = fool.pos_cut

process_list = []

def sub_match(item):
    k,v = item
    if re.match(all_first_name_to_sub_reg,k):
        return "老师",v
    return k,v

def process(res,ll):
    insert_list = []
    for rr,sent in zip(res,ll):
        this_item = {}
        this_item['sent'] = sent
        temp_dict = {k.replace(".","").replace("$",""):v for k,v in rr if not v.startswith("w")}
        temp_dict = dict(map(sub_match,temp_dict.items()))
        this_item['words_pos'] = temp_dict
        this_item['all_words'] = [k for k,v in temp_dict.items() if not v.startswith("w")] # 过滤掉标点符号
        insert_list.append(this_item)
    return insert_list


for line in tqdm(lines):
    if len(process_list) % 10000 == 0 and len(process_list) != 0:
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
    res = fool.pos_cut(process_list)
    insert_list = process(res,process_list)
    cut_word_pos_col.insert_many(insert_list)
    process_list.clear()

