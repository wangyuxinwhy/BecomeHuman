#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:43
# @Author  : yuxin.wang
# @File    : check.py
# @Project : BecomeHuman

import numpy as np

from zongheng.api import api_user_info


class Check:

    description = 'default'

    def __init__(self, web, user):
        self.description = self.__class__.description
        self.web = web
        self.user = user

    def check(self):
        pass


class CheckLogin(Check):

    description = '检验登录'

    def check(self):
        if self.web.is_login:
            return True


class CheckUserName(Check):
    description = '检验用户名是否存在'

    def check(self):
        if self.user.username:
            return True


class CheckPassword(Check):
    description = '检验用户密码是否存在'

    def check(self):
        if self.user.password:
            return True


class CheckWebDriver(Check):
    description = '检验web driver'

    def check(self):
        if self.web.web_driver:
            return True


class CheckCookies(Check):
    description = '检验Cookies'

    def check(self):
        if self.user.cookies:
            return True


class CheckRecomment(Check):
    description = '检验推荐票'

    def check(self):
        recommend_counts = api_user_info(self.user, 'recomment')
        if recommend_counts > 0:
            return True


# checkList返回信息构成
def get_exception_info_from_checklist(checklist, checklist_description):
    exception_info = ''
    index_list = np.array(checklist) == 0
    for index, value in enumerate(index_list):
        if value:
            exception_info += '{}|未通过 '.format(checklist_description[index])
    return exception_info


if __name__ == '__main__':
    pass
