"""
用来对经过clean过滤后的数据做进一步的过滤,过滤掉全是重复字符的和全是字母构成的评论,以及将句子按字去重后，数量小于3的评论
增加is_filter_clean_step1标志，如果为true，则说明是需要删除的评论
"""
from config import clean_col,data_path
from pymongo import UpdateOne
from tqdm import tqdm
import re
from io import StringIO

reg1 = r"^(.)\1{10,}$" # 用来过滤全是重复的字符，比如啊啊啊啊啊啊
reg2 = r"^[0-9a-zA-Z]{10,}$" # 用来过滤全是字母数字的评论，比如ashduaidhuashdu，或者123131312

file1,file2 = StringIO(),StringIO()

dup_log_file = data_path.joinpath("cache_res","dup_log")
all_alphabeta_file = data_path.joinpath("cache_res","all_alphabeta")

dup_count = 0
alphabeta_count = 0
update_op = []

for item in tqdm(clean_col.find({"clean_ext":False},{"pjxx":True})):
    if len(update_op) % 20000 == 0 and len(update_op) != 0:
        clean_col.bulk_write(update_op)
        update_op.clear()
    content = item.get("pjxx").strip()
    _id = item.get("_id")
    flag = False
    if re.search(reg1,content): # 过滤掉全是重复字符的和全是字母构成的评论
        flag = True
        dup_count += 1
        file1.write("%s\n"%content)
    if re.search(reg2,content): # 用来过滤全是字母数字的评论，比如ashduaidhuashdu，或者123131312 
        flag = True
        alphabeta_count += 1
        file2.write("%s\n" % content)
    if not flag and len(set(content)) <= 3: # 用来过滤重复词语的评论，比如很好很好很好很好
        flag = True
        dup_count += 1
        file1.write("%s\n"%content)
    update_op.append(UpdateOne({"_id":_id},{"$set":{"is_filter_clean_step1":flag}}))

if len(update_op) != 0:
    clean_col.bulk_write(update_op)


print("dupcount %s, alpha_count %s" % (dup_count,alphabeta_count))
set_dup = set(filter(None,file1.getvalue().split("\n")))
set_alpha = set(filter(None,file2.getvalue().split("\n")))
print("dupcount set %s, alpha_count set %s" % (len(set_dup),len(set_alpha)))

dup_log_file.write_text(file1.getvalue())
all_alphabeta_file.write_text(file2.getvalue())





