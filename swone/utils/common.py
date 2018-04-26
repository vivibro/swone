# -*- coding:utf-8 -*-
import hashlib


def get_md5(url):
    # 获取md5
    if isinstance(url,str):
        url = url.encode('utf-8')      #hash不支持unicode 需要判断url是否是str(Unicode)做一个转化
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest() #抽取摘要

