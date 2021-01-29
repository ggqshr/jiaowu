import fool
from tqdm import tqdm
import re
import sys
sys.path.append("..")
from prepare.config import db
from pathlib import Path

cut_word_pos_col = db.get_collection("pos_words")

data_path = Path("../data/all_text.txt")
content = data_path.read_text(encoding="utf-8")
lines = list(filter(None,map(lambda x:x.strip(),content.split("\n")))) 

cut_func = fool.pos_cut

process_list = []
for line in tqdm(lines):
    if len(process_list) % 1000 == 0 and len(process_list) != 0:
        res = cut_func(process_list)
        insert_list = []
        for rr,sent in zip(res,process_list):
            this_item = {}
            this_item['sent'] = sent
            temp_dict = {k.replace(".",""):v for k,v in rr if not v.startswith("w")}
            this_item['words_pos'] = temp_dict
            this_item['all_words'] = [k for k,v in temp_dict.items() if not v.startswith("w")] # 过滤掉标点符号
            insert_list.append(this_item)
        cut_word_pos_col.insert_many(insert_list)
        process_list.clear()
    this_line = line.strip()
    this_line = re.sub("\s+", "", this_line)
    if len(this_line) == 0:
        continue
    process_list.append(line)

if len(process_list) != 0:
    res = fool.pos_cut(process_list)
    insert_list = []
    for rr,sent in zip(process_list,res):
        this_item = {}
        this_item['sent'] = sent
        temp_dict = {k:v for k,v in rr}
        this_item['words_pos'] = temp_dict
        this_item['all_words'] = [k for k,v in temp_dict.items() if v.startswith("w")] # 过滤掉标点符号
        insert_list.append(this_item)
    cut_word_pos_col.insert_many(insert_list)
    process_list.clear()

