"""
将数据库中的所有文本去重后导出到文件中，用于下一步的步骤，
"""
from config import clean_col,data_path
from tqdm import tqdm

with open(data_path.joinpath("all_text.txt"),'w',encoding="utf-8") as f:
    group = {}
    group["_id"] = "$pjxx"
    res = clean_col.aggregate([{"$group":group}])
    for item in tqdm(res):
        text = item.get("_id")
        if text is None or text == "" or text.replace(" ","") == "" :
            continue
        f.write("%s\n" % text)
