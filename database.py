#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 10:42
# @Author  : yuxin.wang
# @File    : database.py
# @Project : BecomeHuman

from config import MONGO_URL, MONGO_USERNAME, MONGO_PASSWORD, MONGO_CHAPTER_COLLECTIONS, MONGO_NOVEL_COLLECTIONS,\
    MONGO_USER_ACTION_COLLECTIONS, MONGO_DB_NAME, MONGO_USER_COLLECTIONS
import pymongo

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
import redis


MONGO_CLIENT = pymongo.MongoClient(MONGO_URL, username=MONGO_USERNAME, password=MONGO_PASSWORD, connect=False)
REDIS_CLIENT = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

def get_novel_collections():
    return MONGO_CLIENT[MONGO_DB_NAME][MONGO_NOVEL_COLLECTIONS]


def get_chapter_collections():
    return MONGO_CLIENT[MONGO_DB_NAME][MONGO_CHAPTER_COLLECTIONS]


def get_user_collections():
    return MONGO_CLIENT[MONGO_DB_NAME][MONGO_USER_COLLECTIONS]


def get_user_action_collections():
    return MONGO_CLIENT[MONGO_DB_NAME][MONGO_USER_ACTION_COLLECTIONS]