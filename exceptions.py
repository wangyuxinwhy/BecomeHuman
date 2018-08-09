#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 10:51
# @Author  : yuxin.wang
# @File    : exceptions.py
# @Project : BecomeHuman

class RequestError(Exception):
    pass


class NotifyError(Exception):
    pass


class UserFormatError(Exception):
    pass


class IdentifyCodeError(Exception):
    pass


class WebFunctionError(Exception):
    pass


class LoginError(WebFunctionError):
    pass


class ContextError(WebFunctionError):
    pass


class ConcreteRunError(WebFunctionError):
    pass