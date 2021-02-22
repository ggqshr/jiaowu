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
    for index in range(0,start-1):
        par = dep[index]
        parent = par[1]
        rel = par[2]
        count = 0 # 防止死循环
        while parent <= start and count < 10:
            count += 1
            if rel in ['ATT','ADV']:
                if parent == start:
                    return ("".join(words_origin[index:start-1]),end_word,start_pos,end_pos,rel,index,end,"att&adv")
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
            return ("".join(words_origin[start:index+1]),end_word,start_pos,end_pos,rel,start,end,"coo")

def rule_11(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    for index in range(0,start-1):
        par = dep[index]
        parent = par[1]
        rel = par[2]
        count = 0 # 防止死循环
        while parent <= start and count < 10:
            count += 1
            if rel in ['ATT','ADV','SBV','FOB']:
                if parent == start:
                    return ("".join(words_origin[index:start]),end_word,start_pos,end_pos,rel,index,end,"v_att&adv&sbv&fob")
                else:
                    this_par = dep[parent-1]
                    parent = this_par[1]
                    rel = this_par[2]
            else:
                break

def rule_12(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    for index in range(start-1,end-1):
        par = dep[index]
        if par[1] == start and par[2] in ['COO','VOB']:
            return ("".join(words_origin[start-1:index+1]),end_word,start_pos,end_pos,rel,start,end,"v_coo&vob")

def rule_13(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    for index in range(0,end-1):
        par = dep[index]
        parent = par[1]
        rel = par[2]
        count = 0 # 防止死循环
        while parent <= end and count < 10:
            count += 1
            if rel in ['ATT','ADV']:
                if parent == end:
                    return (start_word,"".join(words_origin[index:end]),start_pos,end_pos,rel,index,end,"a_att")
                else:
                    this_par = dep[parent-1]
                    parent = this_par[1]
                    rel = this_par[2]
            else:
                break

def rule_14(dep,pos_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    ii = end
    word_res = ""
    while ii < len(pos_origin):
        word,pos = pos_origin[ii]
        if pos == 'a':
            word_res += word
            ii += 1
        else:
            break
    return (start_word,end_word+word_res,start_pos,end_pos,rel,start,end,"a_a")

def rule_15(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    return rule_13(dep,words_origin,start_word,end_word,start_pos,end_pos,rel,start,end)

def rule_16(dep,pos_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    word_res = ""
    if end_word in ['是','有','没有','算'] and end < len(dep):
        for index in range(end,len(dep)):
            _,e,rel = dep[index]
            c_word,c_pos = pos_origin[index]
            if e == end and rel == 'VOB' and c_pos == 'd':
                if index < (len(dep) - 1):
                    n_word,n_pos = pos_origin[index+1]
                    if n_pos in ['n','v']:
                        word_res += (end_word + c_word + n_word)
                        return (start_word,word_res,start_pos,end_pos,rel,start,end,'v_d_n/v')

def rule_17(dep,pos_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    word_res = ""
    if end_word in ['是','有','没有','算'] and end < len(dep):
        for index in range(end,len(dep)):
            _,e,rel = dep[index]
            c_word,c_pos = pos_origin[index]
            if e == end and rel == 'VOB' and c_pos == 'd':
                if index < (len(dep) - 1):
                    ii = index + 1
                    n_word,n_pos = pos_origin[ii]
                    if n_pos == 'a':
                        word_res += (end_word+c_word+n_word)
                        return (start_word,word_res,start_pos,end_pos,rel,start,end,'v_d+_a')
                    temp = []
                    while n_pos == 'd':
                        temp.append(n_word)
                        ii += 1
                        if ii < len(dep):
                            n_word,n_pos = pos_origin[ii]
                        else:
                            break
                    if ii < (len(dep) - 1):
                        ii += 1
                        ww,pp = pos_origin[ii]
                        if pp == 'a':
                            word_res += (end_word+c_word+"".join(temp)+ww)
                            return (start_word,word_res,start_pos,end_pos,rel,start,end,'v_d+_a')

def rule_18(dep,pos_origin,start_word,end_word,start_pos,end_pos,rel,start,end):
    """
    v--->(d)+i/v/a
     (VOB)
    """
    word_res = ""
    if end < len(dep):
        for index in range(end,len(dep)): # 从评价词后找依赖于评价词关系为VOB且词性为d的词语
            _,e,rel = dep[index]
            c_word,c_pos = pos_origin[index]
            if e == end and rel == 'VOB' and c_pos == 'd':
                if index < (len(dep) - 1): # 如果有，则继续往下面找词性为d的词语
                    ii = index + 1
                    n_word,n_pos = pos_origin[ii]
                    if n_pos != "d" and n_pos in ['i','v','a']:
                        word_res += (end_word+c_word+n_word)
                        return (start_word,word_res,start_pos,end_pos,rel,start,end,'v_d+_i/v/a')
                    temp = []
                    while n_pos == 'd':
                        temp.append(n_word)
                        ii += 1
                        if ii < len(dep):
                            n_word,n_pos = pos_origin[ii]
                        else:
                            break
                    if ii < (len(dep) - 1):# 如果ii还没到最后，则判断是否为指定的词性
                        ii += 1
                        ww,pp = pos_origin[ii]
                        if pp in ['i','v','a']:
                            word_res += (end_word+c_word+"".join(temp)+ww)
                            return (start_word,word_res,start_pos,end_pos,rel,start,end,'v_d+_i/v/a')

for item in all_items:
    _id = item.get("_id")
    dep = item.get("dep")
    pos_origin = item.get("origin_pos")
    words_origin = item.get("all_words_origin")
    sent = item.get("sent")
    res_table1 = []
    # table 4
    for dd in dep:
        start,end,rel = dd
        start_pos,end_pos,start_word,end_word = get_relationship(pos_origin,start,end)
        for rule in all_table1_rule:
            if rule(start_pos,end_pos,rel):
                res_table1.append((start_word,end_word,start_pos,end_pos,rel,start,end))
    print("sent : %s" % sent)
    print(" comment_obj: %s" % (res_table1) )
    completion_obj_res = []
    for item in res_table1:
        start_word,end_word,start_pos,end_pos,rel,start,end = item
        if start_pos == 'n':
            before_com = ""
            res = rule_9(dep,words_origin,*item)
            if res:
                before_com = res[0]

            after_com = ""
            res = rule_10(dep,words_origin,*item)
            if res:
                after_com = res[0]
            this_res = [before_com + start_word + after_com]
            this_res.extend(list(item)[1:])
            completion_obj_res.append(tuple(this_res))
    print(" completion_obj_res : %s" % completion_obj_res)
    # res_rule_coo = []
    # res_rule_att = []
    # res_rule_v_att = []
    # res_rule_v_coo = []
    # res_rule_end_a_att = []
    # res_rule_end_v_att = []
    # res_rule_end_a_aa = []
    # res_rule_end_v_d__n_or_v = []
    # res_rule_end_v_ddd_a = []
    # res_rule_end_v_ddd__a_or_i_or_v = []
    # for item in res_table1:
    #     start_pos = item[2]
    #     end_pos = item[3]
    #     if start_pos == "n":
    #         # coo
    #         res = rule_10(dep,words_origin,*item)
    #         if res:
    #             res_rule_coo.append(res)

    #         # att & adv
    #         res = rule_9(dep,words_origin,*item)
    #         if res:
    #             res_rule_att.append(res)
    #     elif start_pos == 'v':
    #         # att & adv & sbv & fob
    #         res = rule_11(dep,words_origin,*item)
    #         if res:
    #             res_rule_v_att.append(res)

    #         res = rule_12(dep,words_origin,*item)
    #         if res:
    #             res_rule_v_coo.append(res)
    #     if end_pos == 'a':
    #         res = rule_13(dep,words_origin,*item)
    #         if res:
    #             res_rule_end_a_att.append(res)

    #         res = rule_14(dep,pos_origin,*item)
    #         if res:
    #             res_rule_end_a_aa.append(res)
    #     elif end_pos == 'v':
    #         res = rule_15(dep,words_origin,*item)
    #         if res:
    #             res_rule_end_v_att.append(res)

    #         res = rule_16(dep,pos_origin,*item)
    #         if res:
    #             res_rule_end_v_d__n_or_v.append(res)

    #         res = rule_17(dep,pos_origin,*item)
    #         if res:
    #             res_rule_end_v_ddd_a.append(res)

    #         res = rule_18(dep,pos_origin,*item)
    #         if res:
    #             res_rule_end_v_ddd__a_or_i_or_v.append(res)
    # print(" coo_comment_obj: %s" % (res_rule_coo) )
    # print(" att_comment_obj: %s" % (res_rule_att) )
    # print(" v_att_comment_obj: %s" % (res_rule_v_att) )
    # print(" v_coo_comment_obj: %s" % (res_rule_v_coo) )
    # print(" res_rule_end_a_att: %s" % (res_rule_end_a_att) )
    # print(" res_rule_end_a_aa: %s" % (res_rule_end_a_aa) )
    # print(" res_rule_end_v_att: %s" % (res_rule_end_v_att) )
    # print(" res_rule_end_v_d__n_or_v: %s" % (res_rule_end_v_d__n_or_v) )
    # print(" res_rule_end_v_ddd_a: %s" % (res_rule_end_v_ddd_a) )
    print(" res_rule_end_v_ddd__a_or_i_or_v: %s" % (res_rule_end_v_ddd__a_or_i_or_v) )


