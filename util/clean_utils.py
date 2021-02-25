"""
一些用来处理文本的工具合集
"""
import re
import sys
sys.path.append("..")
from prepare.config import db


teacher_info = db.get_collection("JSXXB")
all_teacher_name = [i.get("xm") for i in teacher_info.find({},{"xm":True,"_id":False}) if len(bytes(i.get("xm")[0],"utf-8")) != 1] # 只取中文的老师
all_teacher_name = [re.sub(r"([\(（].*?[\)）]|\s)","",i) for i in all_teacher_name]
all_first_name = [i[0] for i in all_teacher_name]
all_first_name = set(filter(lambda x:not ('a' <= x <= 'z'),map(lambda x:x.lower(),all_first_name)))

all_first_name_to_sub_reg = "(%s)老师" % "|".join(all_first_name)

def sub_match(item):
    """
    将 李老师 这种词语替换成 老师 
    """
    k,v = item
    if re.match(all_first_name_to_sub_reg,k):
        return "老师",v
    return k,v
