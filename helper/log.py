#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:04
# @Author  : yuxin.wang
# @File    : log.py
# @Project : BecomeHuman


import logging
import yaml
import logging.config
import os

from config import LOGGER_CONFIG_PATH

def setup_logging(default_path=LOGGER_CONFIG_PATH, default_level=logging.INFO):
    if os.path.exists(default_path):
        with open(default_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger('general')
    logger.info('test')