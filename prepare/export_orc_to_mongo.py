from pymongo import MongoClient
from tqdm import tqdm
import pandas as pda
from sqlalchemy import create_engine

client = MongoClient("116.56.140.195",27017)
db = client.get_database("jiaowu")

connect=create_engine('oracle://JWC_ROOT:JWC_ROOT@116.56.140.211:1521/B7310oracle')

all_table = ["CJB",
        "JSXXB",
        "JXRWB",
        "XSJBXXB",
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
        "XSXKBO",]
#for item in data.iterrows():
#    print(item)

def yield_items(data):
    for item in data.iterrows():
        yield item[1].to_dict()

for table in tqdm(all_table):
    col = db.get_collection(table)
    sql = f"select * from {table}"
    data = pda.read_sql(sql,connect)
    col.insert_many(yield_items(data))
