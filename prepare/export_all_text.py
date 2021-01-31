"""
将数据库中的所有文本去重后导出到文件中，用于下一步的步骤，
"""
from config import clean_col,data_path,r_client,db
from tqdm import tqdm
import re
from itertools import chain

data_list = set()

teacher_info = db.get_collection("JSXXB")
all_teacher_name = [i.get("xm") for i in teacher_info.find({},{"xm":True,"_id":False}) if len(bytes(i.get("xm")[0],"utf-8")) != 1] # 只取中文的老师
all_teacher_name = [re.sub(r"([\(（].*?[\)）]|\s)","",i) for i in all_teacher_name]
all_first_name = [i[0] for i in all_teacher_name]
all_first_name = set(filter(lambda x:not ('a' <= x <= 'z'),map(lambda x:x.lower(),all_first_name)))

all_first_name_to_sub_reg = "(%s)老师" % "|".join(all_first_name)
all_name_teacher_to_sub_reg = "(%s)老师" % "|".join(all_teacher_name)
all_name_to_sub_reg = "(%s)" % "|".join(all_teacher_name)


with open(data_path.joinpath("all_text.txt"),'w',encoding="utf-8") as f:
    for item in tqdm(clean_col.find({"clean_ext":False,"is_filter_clean_step1":False},{"pjxx":True})):
        if len(data_list) != 0 and len(data_list) % 10000 == 0:
            f.write("\n".join(data_list))
            data_list.clear()
        content = item.get("pjxx")

        # 将所有的类似“刘老师|刘星老师|刘星”之类的文本替换成老师
        # content = re.sub(all_first_name_to_sub_reg,"老师",content)
        content = re.sub(all_name_teacher_to_sub_reg,"老师",content)
        content = re.sub(all_name_to_sub_reg,"老师",content)
        
        data_list.add(content)

    if len(data_list) != 0:
        f.write("\n".join(data_list))
