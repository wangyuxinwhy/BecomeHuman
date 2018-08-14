#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:02
# @Author  : yuxin.wang
# @File    : utils.py
# @Project : BecomeHuman

import re
import time
import hashlib
import random
from datetime import datetime
import datetime as dt

import requests
from lxml.html import fromstring
import simplejson as json

from helper.file_manager import Bucket
from __version__ import __version__, __author__, __title__
from config import YIMA_TOKEN, YIMA_ITEM_ID
from web_user import get_user_action_stat
from exceptions import RequestError


def get_proxy(test_url='http://www.zongheng.com/'):
    r = requests.get('http://webapi.http.zhimacangku.com/getip?'
                     'num=1&type=2&pro=&city=0&yys=0&port=1&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=').json()
    if r['code'] == 0:
        proxy = '{}:{}'.format(r['data'][0]['ip'], r['data'][0]['port'])
        try:
            requests.get(test_url, proxies={'http': proxy}, timeout=8)
            return proxy
        except Exception:
            return get_proxy()
    else:
        raise Exception('未成功获取代理IP')


# 解析Cookies_dict成string
def cookies_dict_list_to_str(dict_list):
    """
    将字典列表转换成字符串，往往应用在selenium获得cookies后，转为可存储的字符串
    :param dict_list: list
    :return: str
    """
    if dict_list:
        if isinstance(dict_list, list):
            dict_list = dict_list
            r = []
            for d in dict_list:
                k = d['name']
                v = d['value']
                r.append('{}={}; '.format(k, v))
            return ''.join(r)[:-2]


def convert_timestamp(timestamp, fmt='%Y-%m-%d %H:%M'):
    return datetime.strftime(datetime.fromtimestamp(timestamp), fmt)


def is_today(timestamp):
    day1 = convert_timestamp(timestamp, '%Y-%m-%d')
    day2 = datetime.strftime(datetime.today(), '%Y-%m-%d')
    if day1 == day2:
        return True


def today_timestamp_range():
    today = datetime.today()
    start = int(datetime.timestamp(datetime(today.year, today.month, today.day)))
    tomorrow = today + dt.timedelta(days=1)
    end = int(datetime.timestamp(datetime(tomorrow.year, tomorrow.month, tomorrow.day)))
    return (start, end)


def get_phone_num():
    params = {
        'action': 'getmobile',
        'token': YIMA_TOKEN,
        'itemid': YIMA_ITEM_ID
    }
    url = 'http://api.fxhyd.cn/UserInterface.aspx'
    resp = requests.get(url, params).text
    if resp.startswith('success'):
        phone_num = resp.split('|')[1]
        return phone_num
    else:
        raise Exception('未成功获取手机号')


def get_phone_message(phone_num, timeout=60):
    params = {
        'action': 'getsms',
        'token': YIMA_TOKEN,
        'itemid': YIMA_ITEM_ID,
        'mobile': phone_num,
        'release': 1
    }
    url = 'http://api.fxhyd.cn/UserInterface.aspx'
    run_time = 0
    while run_time <= timeout:
        resp = requests.get(url, params).content.decode('utf-8')
        if resp.startswith('success'):
            content = resp.split('|')[1]
            print(content)
            pattern = '验证码：(.*?)，'
            code = re.findall(pattern, content)[0]
            return code
        else:
            time.sleep(5)
            run_time += 5
    raise Exception('未正确获取验证码')


def get_random_nick_name():
    with open('D:\\6_文件\\project_X\\Project_X_001\\name.txt', 'r', encoding='utf-8') as f:
        data = f.readlines()
    return random.choice(data).strip()


def get_register_info(phone_num):
    hash_handler = hashlib.md5()
    hash_handler.update(str.encode(str(phone_num)))
    password = hash_handler.hexdigest()[:10]
    nickname = get_random_nick_name()

    return password, nickname


def update_config_to_aliyun():
    b = Bucket()
    obj_name = 'BecomeHuman/config_v_{}.py'.format(__version__)
    b.put_file(obj_name, '../config.py')


def get_config_from_aliyun():
    b = Bucket()
    obj_name = 'BecomeHuman/config_v_{}.py'.format(__version__)
    b.get_file(obj_name, '../config.py')


def get_yima_account_info():
    """
    易码平台账户信息，关键字段 (余额, "Balance")
    :return: dict
    """
    params = {
        'action': 'getaccountinfo',
        'token': YIMA_TOKEN,
        'format': 1
    }
    url = 'http://api.fxhyd.cn/UserInterface.aspx'
    resp = requests.get(url, params=params).text
    status, data = resp.split('|')
    if status == 'success':
        data = json.loads(data)
        return {'account_type': '易码', 'Balance': data['Balance']}
    else:
        raise RequestError('request Failed')


def get_chaojiying_account_info():
    url = 'http://www.chaojiying.com/user/'
    headers = {
        'Cookie': 'PHPSESSID=nph5rfgdi8bapttepuitcd1124; __51cke__=; __tins__16851773=%7B%22sid%22%3A%201534229980189%2C%20%22vd%22%3A%208%2C%20%22expires%22%3A%201534231828194%7D; __51laig__=8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    resp = requests.get(url, headers=headers)
    html = fromstring(resp.content)
    balance = html.xpath('/html/body/div[3]/div[2]/div[1]/div[1]/span')[0].text
    return {'account_type': '超级鹰', 'Balance': balance}


def get_zhimahttp_account_info():
    url = 'http://web.http.cnapi.cc/index/index/get_my_balance?neek=49624&appkey=9a6e35aae3eccaedd72119c1a3e888b6'
    resp = requests.get(url).json()
    return {'account_type': '芝麻HTTP', 'Balance': resp['data']['balance']}


def get_project_info():
    title = __title__
    version = __version__
    author = __author__
    balance = [get_chaojiying_account_info(), get_zhimahttp_account_info(), get_yima_account_info()]
    start, end = today_timestamp_range()
    user_action_success = get_user_action_stat(start, end, 1)
    user_action_failed = get_user_action_stat(start, end, 0)
    info = """==== Project Info ====\n
>>>> Base Info <<<<
name:   \t{title}
version: \t{version}
author: \t{author}
\n
>>>> user action success <<<<
{success}
\n
>>>> user action failed <<<<
{failed}
\n
>>>> balance <<<<
{balance}
    """.format(title=title, version=version, author=author,
               success=user_action_success, failed=user_action_failed, balance=balance)
    return info


if __name__ == '__main__':
    print(get_project_info())
