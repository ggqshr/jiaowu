"""
将数据库中的所有文本去重后导出到文件中，用于下一步的步骤，
"""
from config import clean_col,data_path,r_client
from tqdm import tqdm

data_list = set()

with open(data_path.joinpath("all_text.txt"),'w',encoding="utf-8") as f:
    for item in tqdm(clean_col.find({"clean_ext":False,"is_filter_clean_step1":False},{"pjxx":True})):
        if len(data_list) != 0 and len(data_list) % 10000 == 0:
            f.write("\n".join(data_list))
            data_list.clear()
        data_list.add(item.get("pjxx"))

    if len(data_list) != 0:
        f.write("\n".join(data_list))
