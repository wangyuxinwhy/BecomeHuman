#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 13:27
# @Author  : yuxin.wang
# @File    : main.py
# @Project : BecomeHuman


import logging
from copy import deepcopy

from celery import Celery
from celery.schedules import crontab
import numpy as np
from datetime import datetime
import datetime as dt
import time

from web import Web
from web_user import User, get_random_user, get_sequence_user
from helper.log import setup_logging
from helper.utils import is_today, get_proxy
from zongheng.schdule_support import get_random_comment, get_book_from_id, get_random_book_id, get_random_chapter_id
from zongheng.web_function import Login, LoginWithCookies, ReadBook, CollectBook, BookComment, ChapterComment, Register, RecommendBook
from zongheng.web_function_support import FUNCTION_CHAPTER_COMMENT_CONFIG, FUNCTION_BOOK_COMMENT_CONFIG
from zongheng.api import api_user_info
from config import NOVEL_TITLE, NOVEL_DESCRIPTION, WEBDRIVER_HEADLESS
from __version__ import __title__, __version__, __author__

setup_logging()
logger = logging.getLogger('general')

app = Celery('main', broker='redis://localhost/1')
app.conf.timezone = "Asia/Shanghai"
app.conf.beat_schedule = {
    'work_on_daytime': {
        'task': 'main.daily_work',
        'schedule': crontab('10, 20, 30, 40, 50, 55', '8-22'),
        'args': ()
    },
    'work_for_book_comment': {
        'task': 'main.schedule_book_comment',
        'schedule': crontab('10', '8, 16'),
        'args': (5,)
    },
    'work_for_chapter_comment': {
        'task': 'main.schedule_chapter_comment',
        'schedule': crontab('10', '10, 18'),
        'args': (10,)
    }
}


@app.task
def daily_work(headless=WEBDRIVER_HEADLESS):
    """
    日常工作的任务包括登录、收藏及阅读默认的书籍
    :return:
    """
    try:
        # user = User(get_sequence_user())
        user = User('18774448445')
        logger.info('{} ver: {} author: {} worker: {} START DAILY WORK'
                    .format(__title__, __version__, __author__, user.nickname))

        with Web(headless=headless) as chrome:

            user_recomment_num = api_user_info(user, 'recomment')

            if user_recomment_num:
                login = Login(chrome, user)
            elif user.last_work_time and user.cookies:
                if is_today(user.last_work_time):
                    login = LoginWithCookies(chrome, user)
                else:
                    login = Login(chrome, user)
            else:
                login = Login(chrome, user)

            login.run()

            # 收藏
            if user.is_collect == '0':
                func_collect = CollectBook(chrome, user)
                func_collect.run()

            # 推荐
            if user_recomment_num:
                func_recommend = RecommendBook(chrome, user)
                func_recommend.run()

            # 阅读
            func_read = ReadBook(chrome, user)
            func_read.run()
    except Exception:
        logger.error('{}|{} -->'.format('Work', 'FAILED REASON'), exc_info=True)


@app.task
def chapter_comment(user: str, book_id, chapter_id, recommend_book=NOVEL_TITLE,
                    recommend_description=NOVEL_DESCRIPTION, proxy=None, headless=True):
    try:
        user = User(user)
        logger.info('{} ver: {} author: {} worker: {} start chapter comment for "{}"'
                    .format(__title__, __version__, __author__, user.nickname, recommend_book))
        book = get_book_from_id(book_id)

        book_name = book.get('title')
        author = book.get('author')
        book_id = book.get('book_id')
        comment = get_random_comment(book_name, author, recommend_book, recommend_description)

        with Web(proxy=proxy, headless=headless) as chrome:
            if user.cookies:
                LoginWithCookies(chrome, user).run()
            else:
                Login(chrome, user).run()

            conf = deepcopy(FUNCTION_CHAPTER_COMMENT_CONFIG)
            conf['book_id'] = book_id
            conf['chapter_id'] = chapter_id
            conf['comment'] = comment

            ChapterComment(chrome, user, config=conf).run()
    except Exception:
        logger.error('{}|{} -->'.format('Work', 'FAILED REASON'), exc_info=True)


@app.task
def book_comment(user, book_id, recommend_book=NOVEL_TITLE, recommend_description=NOVEL_DESCRIPTION,
                 proxy=None, headless=True):
    try:
        user = User(user)
        logger.info('{} ver: {} author: {} worker: {} start book comment for "{}"'
                    .format(__title__, __version__, __author__, user.nickname, recommend_book))

        book = get_book_from_id(book_id)
        book_name = book.get('title')
        author = book.get('author')

        title = '《{}》前来拜访{}大大'.format(recommend_book, book.get('author'))
        comment = get_random_comment(book_name, author, recommend_book, recommend_description)

        with Web(proxy=proxy, headless=headless) as chrome:
            if user.cookies:
                try:
                    LoginWithCookies(chrome, user).run()
                except Exception:
                    Login(chrome, user).run()
            else:
                Login(chrome, user).run()

            conf = deepcopy(FUNCTION_BOOK_COMMENT_CONFIG)
            conf['book_id'] = book_id
            conf['title'] = title
            conf['comment'] = comment

            BookComment(chrome, user, config=conf).run()

    except Exception:
        logger.error('{}|{} -->'.format('Work', 'FAILED REASON'), exc_info=True)


@app.task
def schedule_book_comment(num):
    proxy = get_proxy()
    for i in range(0, num):
        user = get_random_user()
        book_id = get_random_book_id()
        minutes = np.random.randint(0, 10)
        run_delay = datetime.utcnow() + dt.timedelta(minutes=minutes)
        book_comment.apply_async(args=[user, book_id], kwargs={'proxy': proxy}, eta=run_delay)


@app.task
def schedule_chapter_comment(num):
    proxy = get_proxy()
    for i in range(0, num):
        user = get_random_user()
        book_id = get_random_book_id()
        chapter_id = get_random_chapter_id(book_id)
        minutes = np.random.randint(0, 10)
        run_delay = datetime.utcnow() + dt.timedelta(minutes=minutes)
        chapter_comment.apply_async(args=[user, book_id, chapter_id], kwargs={'proxy': proxy}, eta=run_delay)


@app.task
def register_user():
    with Web(headless=False, proxy=get_proxy()) as chrome:
        Register(chrome).run()
    time.sleep(60)


if __name__ == '__main__':
    # app.start()
    # register_user()
    daily_work(headless=False)
