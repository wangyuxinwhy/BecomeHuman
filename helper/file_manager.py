#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:39
# @Author  : yuxin.wang
# @File    : file_manager.py
# @Project : BecomeHuman

from itertools import islice

import oss2

from config import ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET


class Bucket:

    auth = oss2.Auth(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET)
    endpoint = 'http://oss-cn-beijing.aliyuncs.com'

    def __init__(self, bucket_name='yuxin-wang'):
        self.bucket_name = bucket_name
        self.bucket = self.get_bucket()

    def get_bucket(self):
        bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        return bucket

    def put_file(self, object_name, file_path):
        return self.bucket.put_object_from_file(object_name, file_path)

    def get_file(self, object_name, file_path):
        return self.bucket.get_object_to_file(object_name, file_path)

    def delete_file(self, object_name):
        return self.bucket.delete_object(object_name)

    def exist(self, object_name):
        return self.bucket.object_exists(object_name)

    def iter_file(self, num=10):
        file_list = []
        for obj in islice(oss2.ObjectIterator(self.bucket), num):
            file_list.append(obj.key)
        return file_list

    def show_files(self):
        print(self.iter_file(30))


if __name__ == '__main__':
    b = Bucket()
    b.show_files()
