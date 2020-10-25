from pymongo import MongoClient
import pandas as pda
from sqlalchemy import create_engine

client = MongoClient("116.56.140.195",27017)
db = client.get_database("jiaowu")

connect=create_engine('oracle://CRM_GZ_INST:CRM_GZ_INST@116.56.140.211:1521/B7310oracle')
sql = "select * from XS201020111"

data = pda.read_sql(sql,connect)
print(data.describe())


