"""
配置文件，用于配置数据库的连接和一些路径等
"""
from pymongo import MongoClient
from pprint import pprint
from tqdm import tqdm
from threading import Thread
from queue import Queue,Empty
import re
from pathlib import Path
from redis import Redis

client = MongoClient("116.56.140.195",27017)
db = client.get_database("jiaowu")
clean_col = db.get_collection("simple_clean_pjxx")


data_path = Path("../data")

r_client = Redis("116.56.140.195",decode_responses=True)
