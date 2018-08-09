#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:43
# @Author  : yuxin.wang
# @File    : api.py
# @Project : BecomeHuman

from collections import namedtuple

import requests
import simplejson as json

from helper.utils import cookies_dict_list_to_str

API = namedtuple('API', ['method', 'url', 'data'])

# API
API_BOOK_UPDATE = API('POST', 'http://book.zongheng.com/book/async/info.htm', {'bookId': 755129})
API_BOOK_COMMENT = API('POST', 'http://book.zongheng.com/api/book/comment/getThreadL1st2.htm', {'bookId': 755129,
                                                                                                'pagebar': 0,
                                                                                                'pageNum': 1,
                                                                                                'PageSize': 30})
API_CHAPTER_COMMENT = API('GET', 'http://book.zongheng.com/api/book/comment/getThreadL1st3.htm', {'bookId': 755129,
                                                                                                  'chapterId': 41711093,
                                                                                                  'pageNum': 1,
                                                                                                  'pageSize': 10})
API_USRE_INFO = API('GET', 'http://www.zongheng.com/api/user/info.htm', None)


def get_api_response(api, isjson=False, **kwargs):

    resp = requests.request(api.method, api.url, **kwargs)

    if resp.ok:
        if isjson:
            return resp.json()
        else:
            return resp.text
    else:
        raise Exception('Request API Error')


def api_user_info(user, key='__all'):
    """
    返回用户在纵横中文网中的信息
    :param user: User
    :param key: str 'all' -> 返回完整信息 ['level', 'userLevelScore', 'memeberTicket', 'recomment'] 返回信息中该key的值
    :return: object
    """
    headers = {
        'Cookie': cookies_dict_list_to_str(user.cookies)
    }
    resp = get_api_response(API_USRE_INFO, headers=headers)
    resp_dict = json.loads(resp)
    if key == '__all':
        return resp_dict
    else:
        return resp_dict[key]


def api_book_latest_chapter(book_id, key='__all'):
    data = {'bookId': book_id}
    resp = get_api_response(API_BOOK_UPDATE, isjson=True, data=data)
    if key == '__all':
        return resp
    else:
        return resp[key]


def api_book_chapter_comment(book_id, chapter_id):
    params = {
        'bookId': int(book_id),
        'chapterId': int(chapter_id),
        'pageNum': 1,
        'pageSize': 10
    }

    resp = get_api_response(API_CHAPTER_COMMENT, params=params, isjson=True)
    return resp


def api_book_comment(book_id):
    params = {'bookId': book_id, 'pagebar': 0, 'pageNum': 1, 'pageSize': 30}

    resp = get_api_response(API_BOOK_COMMENT, params=params)
    return resp


if __name__ == '__main__':
    print('独步逍遥0203' in api_book_comment(757864))
