"""
用来清洗数据使用的代码，将教评数据进行简单的清洗，然后存入到一个数据库中,不减少任何字段
存入到simple_clean_pjxx中
write 2020.11.21 15:04
"""
from pymongo import MongoClient
from pprint import pprint
from tqdm import tqdm
import re

f_list= [
re.compile("(老师教学认真负责，关心我的课程学习状况).*?(老师教学认真负责，关心我的课程学习状况)*"),
re.compile("(老师讲课熟练，清晰易懂).*?(老师讲课熟练，清晰易懂)*"),
re.compile("(老师的授课内容充实，安排合理，重点突出).*?(老师的授课内容充实，安排合理，重点突出)*"),
re.compile("(老师采用多样化的教学方法开展教学，善于启发和引导学生有效激发我的学习兴趣).*?(老师采用多样化的教学方法开展教学，善于启发和引导学生有效激发我的学习兴趣)*"),
re.compile("(老师注重与学生的交流和互动，有良好的交流技巧).*?(老师注重与学生的交流和互动，有良好的交流技巧)*"),
re.compile("(老师课内外均乐于答疑解惑).*?(老师课内外均乐于答疑解惑)*"),
re.compile("(通过该课程的学习，我觉得很有收获).*?(通过该课程的学习，我觉得很有收获)*"),]

client = MongoClient("116.56.140.195",27017)
db = client.get_database("jiaowu")

target_col = db.get_collection("simple_clean_pjxx")

all_col = [
        "XSPFB_201020111",
        "XSPFB_201020112",
        "XSPFB_201120121",
        "XSPFB_201120122",
        "XSPFB_201220131",
        "XSPFB_201220132",
        "XSPFB_201320141",
        "XSPFB_201320142",
        "XSPFB_201420151",
        "XSPFB_201420152",
        "XSPFB_201520161",
        ]


def clean_ext():
    filter_count = 0
    for col_name in all_col:
        this_col = db.get_collection(col_name)
        item_list = []
        for item in tqdm(this_col.find({},no_cursor_timeout=True,batch_size=10000),desc=col_name,):
            if len(item_list) != 0 and len(item_list) % 100000 == 0:
                target_col.insert_many(item_list)
                item_list.clear()
            flag = False
            text = item.get("pjxx","")
            item["clean_ext"] = False
            if text == "" or text is None:
                item['clean_ext'] = True
            else:
                for reg in f_list:
                    if (aa := re.match(reg,text)):
                        item['clean_ext'] = True
                        filter_count += 1
                        break
            item_list.append(item)
        if len(item_list) != 0:
            target_col.insert_many(item_list)
    print(f"{filter_count=}")

if __name__ == '__main__':
    clean_ext()
