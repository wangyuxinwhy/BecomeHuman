#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 10:42
# @Author  : yuxin.wang
# @File    : web_user.py
# @Project : BecomeHuman

import pandas as pd
import random
import numpy as np
from numpy.random import multinomial
from datetime import datetime

from database import get_user_collections, REDIS_CLIENT
from exceptions import UserFormatError

USER_FIELD = {'username': None,
              'password': None,
              'nickname': None,
              'is_collect': 0,
              'last_work_time': None,
              'last_chapter_url': None,
              'cookies': None,
              'is_last_work_success': 1,
              'work_times': 0,
              'work_failed_times': 0}


class User:

    def __init__(self, user_tel: str, website: str = 'zongheng'):
        
        self.check_user_tel(user_tel)
        user_tel = user_tel.strip()
        self.name = website + user_tel
        if not self.exists:
            self.user_init()

    @property
    def exists(self):
        return REDIS_CLIENT.exists(self.name)

    @property
    def username(self):
        return self.get_value_from_db('username')

    @username.setter
    def username(self, value):
        self.set_value_to_db('username', value)

    @property
    def password(self):
        return self.get_value_from_db('password')

    @password.setter
    def password(self, value):
        self.set_value_to_db('password', value)

    @property
    def nickname(self):
        return self.get_value_from_db('nickname')

    @nickname.setter
    def nickname(self, value):
        self.set_value_to_db('nickname', value)

    @property
    def is_collect(self):
        return self.get_value_from_db('is_collect')

    @is_collect.setter
    def is_collect(self, value):
        self.set_value_to_db('is_collect', value)

    @property
    def last_work_time(self):
        value = self.get_value_from_db('last_work_time')
        if value != 'None':
            return int(value)
        else:
            return None

    @last_work_time.setter
    def last_work_time(self, value):
        self.set_value_to_db('last_work_time', value)

    @property
    def cookies(self):
        value = self.get_value_from_db('cookies')
        if value != 'None':
            return eval(value)
        else:
            return None

    @cookies.setter
    def cookies(self, value):
        self.set_value_to_db('cookies', value)

    @property
    def is_last_work_success(self):
        return self.get_value_from_db('is_last_work_success')

    @is_last_work_success.setter
    def is_last_work_success(self, value):
        self.set_value_to_db('is_last_work_success', value)

    @property
    def work_times(self):
        return self.get_value_from_db('work_times')

    @work_times.setter
    def work_times(self, value):
        self.set_value_to_db('work_times', value)

    @property
    def work_failed_times(self):
        return self.get_value_from_db('work_failed_times')

    @work_failed_times.setter
    def work_failed_times(self, value):
        self.set_value_to_db('work_failed_times', value)

    @property
    def last_chapter_url(self):
        return self.get_value_from_db('last_chapter_url')

    @last_chapter_url.setter
    def last_chapter_url(self, value):
        self.set_value_to_db('last_chapter_url', value)

    def user_init(self):
        for field, value in USER_FIELD.items():
            REDIS_CLIENT.hset(self.name, field, value)

    def get_value_from_db(self, key):
        return REDIS_CLIENT.hget(self.name, key)

    def set_value_to_db(self, key, value):
        return REDIS_CLIENT.hset(self.name, key, value)

    @staticmethod
    def check_user_tel(user_tel):
        tel = user_tel
        try:
            int(tel)
        except ValueError as e:
            raise UserFormatError('用户名中包含非法字符') from e

        if len(tel) == 11:
            pass
        else:
            raise UserFormatError('用户名长度不为11')


def show_info_of_user():
    keys_list = REDIS_CLIENT.keys('*')
    info = []
    for i in keys_list:
        if i.startswith('zongheng'):
            info.append(REDIS_CLIENT.hgetall(i))
    df = pd.DataFrame(info)

    def timestamp_convert(value):
        if value != 'None':
            return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    if 'last_work_time' in df.columns.tolist():
        df['last_work_time'] = df['last_work_time'].apply(timestamp_convert)

    return df


def get_random_user(user_list=None):
    """
    得到一个随机的username, 若不输入则总mongodb中取数
    :return: str
    """
    user_col = get_user_collections()
    if not user_list:
        user_list = list(user_col.find({}))
        return str(random.choice(user_list)['username'])
    else:
        return str(random.choice(user_list))


# 按照一定的算法选择一个用户，使得用户工作情况平衡
def get_prob_user():
    df = show_info_of_user()
    s1 = df['work_times'].astype(int)
    s1[s1 == 0] = 1
    s2 = 1 / (s1 / s1.sum())
    prob = s2 / s2.sum()
    prob.iloc[-1] = prob.sum() - prob.iloc[:-1].sum()
    index = np.where(multinomial(1, prob) == 1)[0][0]
    return str(df.loc[index, 'username'])


def get_sequence_user():
    user_col = get_user_collections()
    user_list = list(user_col.find({}))
    user_count = len(user_list)
    index = REDIS_CLIENT.get('worker_index')
    if index is not None:
        index = int(index)
        index += 1
        if index > (user_count - 1):
            index = 0
    else:
        index = 0
    REDIS_CLIENT.set('worker_index', index)
    return str(user_list[index]['username'])


def user_refresh():
    user_col = get_user_collections()
    user_list = list(user_col.find({}))
    for i in user_list:
        user = User(str(i['username']))
        user.username = i['username']
        user.password = i['password']
        user.nickname = i['nickname']


if __name__ == '__main__':
    user_refresh()
