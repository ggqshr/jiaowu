"""
使用规则的方法来获得评论中的评价对象的程序，采用的是
[1].	张璞, 李逍与刘畅, 基于规则的评价搭配抽取方法. 计算机工程, 2019. 45(08): 第217-223页.
的方法
"""
from typing import List
import re
import sys
sys.path.append("..")
from prepare.config import r_client, db

pos_col = db.get_collection("pos_words")

all_items = pos_col.find(
    {}, {"dep": True, "origin_pos": True, "_id": True,"sent":True,"all_words_origin":True}, no_cursor_timeout=True)


def get_relationship(words_pos_list, start, end):
    start_word, start_pos = words_pos_list[start-1]
    if end == 0:
        end_word,end_pos = "None","ROOT"
    else:
        end_word, end_pos = words_pos_list[end-1]
    return start_pos, end_pos, start_word, end_word


def table_4_rule_1(start_pos, end_pos, rel):
    if rel == "SBV" and start_pos == "n" and end_pos == "a":
        return True
    return False


def table_4_rule_2(start_pos, end_pos, rel):
    """
    和论文中不同，start_pos增加了v，为了提取“讲解深入浅出”这种模式
    """
    if rel == "SBV" and (start_pos == "n" or start_pos == 'v') and (end_pos == "d" or end_pos == "i"):
        return True
    return False


def table_4_rule_3(start_pos, end_pos, rel):
    if rel == "SBV" and start_pos == "n" and end_pos == "v":
        return True
    return False


def table_4_rule_4(start_pos, end_pos, rel):
    if rel == "SBV" and start_pos == "v" and end_pos == "a":
        return True
    return False


def table_4_rule_5(start_pos, end_pos, rel):
    if rel == "SBV" and start_pos == "v" and end_pos == "v":
        return True
    return False


def table_4_rule_6(start_pos, end_pos, rel):
    if rel == "CMP" and start_pos == "v" and end_pos == "a":
        return True
    return False


def table_4_rule_7(start_pos, end_pos, rel):
    if rel == "CMP" and start_pos == "v" and end_pos == "d":
        return True
    return False

all_table1_rule = [eval("table_4_rule_%s" % i) for i in range(1,8)]

def rule_9(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    """
    使用ATT或者ADV关系补全评论对象提取
    """
    for index in range(0,start):
        par = dep[index]
        parent = par[1]
        rel = par[2]
        count = 0 # 防止死循环
        while parent <= start and count < 10:
            count += 1
            if rel in ['ATT','ADV']:
                if parent == start:
                    return ("".join(words_origin[index:start]),end_word,start_pos,end_pos,rel,index,end,"att&adv")
                else:
                    this_par = dep[parent-1]
                    parent = this_par[1]
                    rel = this_par[2]
            else:
                break



def rule_10(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    """
    使用coo规则补全评价对象，在评价方面和形容词之间寻找，如果和评论对象是coo关系，那么就把两个词之间所有的词语当作新的补全评价对象
    """
    for index in range(start-1,end-1):
        par = dep[index]
        if par[1] == start and par[2] == 'COO':
            return ("".join(words_origin[start-1:index+1]),end_word,start_pos,end_pos,rel,start,end,"coo")

for item in all_items:
    _id = item.get("_id")
    dep = item.get("dep")
    pos_origin = item.get("origin_pos")
    words_origin = item.get("all_words_origin")
    sent = item.get("sent")
    res_table1 = []
    # table 4 rule 1
    for dd in dep:
        start,end,rel = dd
        start_pos,end_pos,start_word,end_word = get_relationship(pos_origin,start,end)
        for rule in all_table1_rule:
            if rule(start_pos,end_pos,rel):
                res_table1.append((start_word,end_word,start_pos,end_pos,rel,start,end))
    print("sent : %s" % sent)
    # print(" comment_obj: %s" % (res_table1) )
    res_rule_coo = []
    res_rule_att = []
    for item in res_table1:
        if start_pos == "n":
            # coo
            res = rule_10(dep,words_origin,*item)
            if res:
                res_rule_coo.append(res)

            # att & adv
            res = rule_9(dep,words_origin,*item)
            if res:
                res_rule_att.append(res)
    # print(" coo_comment_obj: %s" % (res_rule_coo) )
    print(" att_comment_obj: %s" % (res_rule_att) )


