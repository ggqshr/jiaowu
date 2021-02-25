"""
一些用来处理文本的工具合集
"""
import re
import sys
sys.path.append("..")
from prepare.config import db
from pathlib import Path
from collections import defaultdict

class SubFirstNameMatch:
    """
    用来将 李老师 替换成 老师
    """
    
    all_first_name_to_sub_reg = None
    
    def __init__(self,):
        pass

    def sub_match(self,item):
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
        k,v = item
        if re.match(self.all_first_name_to_sub_reg,k):
            return "老师",v
        return k,v

class FilterStopWord:
    """
    去重停用词
    """
    all_stop_words = list(filter(None,Path(__file__).parent.joinpath("../data/stopwords.txt").read_text(encoding="utf-8").split("\n")))
    filter_map = None

    def filter_stop(self,word):
        if self.filter_map is None:
            self.filter_map = defaultdict(bool)
            for ww in self.all_stop_words:
                self.filter_map[ww] = True
        return self.filter_map[word]