#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 13:36
# @Author  : yuxin.wang
# @File    : schdule_support.py
# @Project : BecomeHuman

import random

from database import get_novel_collections, get_chapter_collections
from zongheng.web_function_support import COMMENT_LIST


def get_random_book(num=1):
    novel_col = get_novel_collections()
    book_list = list(novel_col.find())
    if num == 1:
        return random.choice(book_list)
    else:
        return random.choices(book_list, k=num)


def get_random_book_id(num=1):
    if num == 1:
        return get_random_book(num=1)['book_id']
    else:
        book_id_list = [i['book_id'] for i in get_random_book(num)]
        return book_id_list


def get_random_chapter(book_id, num=1):
    novel_chapter_col = get_chapter_collections()
    chapter_list = list(novel_chapter_col.find({'book_id': str(book_id), 'vip': None}))
    if num == 1:
        return random.choice(chapter_list)
    else:
        return random.choices(chapter_list, k=num)


def get_random_chapter_id(book_id, num=1):
    if num == 1:
        return get_random_chapter(book_id, num=1)['chapter_id']
    else:
        chapter_id_list = [i['chapter_id'] for i in get_random_chapter(book_id, num)]
        return chapter_id_list


def get_book_from_id(book_id):
    novel_col = get_novel_collections()
    book = novel_col.find_one({'book_id': str(book_id)})
    return book


def get_random_comment(book, author, recommend_book, recommend_book_description):
    comment = random.choice(COMMENT_LIST)
    comment = comment.format(book_name=book,
                             author_name=author,
                             recommend_book_name=recommend_book,
                             book_description=recommend_book_description)
    return comment.strip()

if __name__ == '__main__':
    get_random_book()