#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:35
# @Author  : yuxin.wang
# @File    : notify.py
# @Project : BecomeHuman

import logging

from config import IFTTT_NOTIFY_URL
from exceptions import NotifyError

import requests

logger = logging.getLogger('general')


class InfoTrigger:

    def __init__(self, name='消息通知', value_count=2, mode='json'):
        self.name = name
        self.value_count = value_count
        self.type = mode


class Notification:

    def __init__(self, trigger):
        self.trigger = trigger
        self.url = self.get_url()
        self.logger = logger

    def send(self, *args):
        value = {'value{}'.format(i+1): v for i, v in enumerate(args)}
        # if len(value) == self.trigger.value_count:
        if len(value) != 0:
            for i in self.url:
                self.logger.info('{}|{} --> {}'.format('Notify', 'SUCCESS', i))
                requests.post(i, data=value)
        else:
            self.logger.error('{}|{}'.format('Notify', 'FAILED'))
            raise NotifyError('通知的消息不能为空')

    def get_url(self):
        url_format = IFTTT_NOTIFY_URL
        return [i.format(self.trigger.name) for i in url_format]


TRIGGER_CLASS = {
    'InfoTrigger': InfoTrigger()
}


if __name__ == '__main__':
    t = InfoTrigger()
    n = Notification(t)
    n.send('文章更新', '小海的文章更新了')
