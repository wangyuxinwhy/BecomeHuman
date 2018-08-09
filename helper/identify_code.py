#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:02
# @Author  : yuxin.wang
# @File    : identify_code.py
# @Project : BecomeHuman


from hashlib import md5

import requests

from config import CHAOJIYING_KIND, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID, CHAOJIYING_USERNAME
from logging import getLogger
from exceptions import IdentifyCodeError, RequestError

logger = getLogger('general')


class ChaojiyingClient:

    def __init__(self, username=CHAOJIYING_USERNAME, password=CHAOJIYING_PASSWORD, soft_id=CHAOJIYING_SOFT_ID):
        self.username = username
        self.password = md5(password.encode('utf8')).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }
        self.logger = logger

    def post_pic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php',
                          data=params, files=files, headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()

    def parse(self, im):
        result = self.post_pic(im, CHAOJIYING_KIND)
        if result['err_no'] == 0:
            self.logger.info('{}|{} --> {}'.format('Identify Code', 'SUCCESS', result['pic_str']))
            return result['pic_str']
        else:
            self.logger.info('{}|{}'.format('Identify Code', 'FAILED'))
            raise IdentifyCodeError('验证码识别错误')


# 识别验证码
def identify_code_from_url(url):
    """
    给定验证码图片的地址，返回验证码
    :param url: 验证码地址
    :return: str 验码识别结果
    """
    cj = ChaojiyingClient()
    resp = requests.get(url)
    if resp.ok:
        if len(resp.content) < 500:
            raise Exception('未成功获取验证码图片：类型错误')
        return cj.parse(resp.content)
    else:
        raise RequestError('未成功获取验证码图片：请求错误')


def identify_code_from_bytes(value):
    cj = ChaojiyingClient()
    return cj.parse(value)


if __name__ == '__main__':
    # chaojiying = Chaojiying_Client()
    # r = chaojiying.parse('./code_pic/b.jpeg')
    # print(r)
    t = 'https://passport.zongheng.com/passimg?captkey=0b8cddc3de6aeb6897fc3&t=0.6138540865602709'
