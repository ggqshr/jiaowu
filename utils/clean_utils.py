"""
一些用来处理文本的工具合集
"""
import re
import sys
sys.path.append("..")
from prepare.config import db
from pathlib import Path
from collections import defaultdict

all_stop_words = list(filter(None,Path(__file__).parent.joinpath("../data/stopwords.txt").read_text(encoding="utf-8").split("\n")))
filter_map = defaultdict(bool)
for word in all_stop_words:
    filter_map[word] = True

class SubFirstNameMatch:
    """
    用来将 李老师 替换成 老师
    """
    
    all_first_name_to_sub_reg = None
    
    def __init__(self,):
        pass

    def sub_match(self,word):
        """
        将 李老师 这种词语替换成 老师 
        """
        if self.all_first_name_to_sub_reg is None:
            teacher_info = db.get_collection("JSXXB")
            all_teacher_name = [i.get("xm") for i in teacher_info.find({},{"xm":True,"_id":False}) if len(bytes(i.get("xm")[0],"utf-8")) != 1] # 只取中文的老师
            all_teacher_name = [re.sub(r"([\(（].*?[\)）]|\s)","",i) for i in all_teacher_name]
            all_first_name = [i[0] for i in all_teacher_name]
            all_first_name = set(filter(lambda x:not ('a' <= x <= 'z'),map(lambda x:x.lower(),all_first_name)))
            self.all_first_name_to_sub_reg = "(%s)老师" % "|".join(all_first_name)
        if re.match(self.all_first_name_to_sub_reg,word):
            return "老师"
        return word

def filter_stop_words(word):
    return filter_map[word]