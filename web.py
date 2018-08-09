#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:29
# @Author  : yuxin.wang
# @File    : web.py
# @Project : BecomeHuman

import time
import io
from PIL import Image

from config import WEBDRIVER_HEADLESS, WEBDRIVER_PATH

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
import logging
LOGGER.setLevel(logging.CRITICAL)


class Web:

    def __init__(self, proxy: str=None, headless=WEBDRIVER_HEADLESS):
        """
        初始化浏览器，通过调整下列参数来改变浏览器设置
        :param proxy: str eg: '180.120.207.252:29200'
        :param headless: bool
        """
        self._is_login = False
        self.proxy = proxy
        self.headless = headless
        self.web_driver = self.get_web_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.web_driver.close()

    @property
    def is_login(self):
        return self._is_login

    @is_login.setter
    def is_login(self, value):
        if isinstance(value, bool):
            self._is_login = value

    def get_web_driver(self):

        chrome_opt = webdriver.ChromeOptions()

        chrome_opt.add_argument("--log-level=3")

        if self.proxy:
            chrome_opt.add_argument('--proxy-server=http://{}'.format(self.proxy))

        if self.headless:
            args = ['--headless', '--no-sandbox', '--disable-gpu']
            for i in args:
                chrome_opt.add_argument(i)
        else:
            chrome_opt.add_argument('disable-infobars')

        if WEBDRIVER_PATH:
            web_driver = webdriver.Chrome(executable_path=WEBDRIVER_PATH, chrome_options=chrome_opt)
        else:
            web_driver = webdriver.Chrome(chrome_options=chrome_opt)

        web_driver.implicitly_wait(10)
        web_driver.set_window_size(1200, 800)
        web_driver.set_page_load_timeout(300)

        return web_driver

    def get_element(self, element):
        """
        通过 CSS Selector 获取网页元素
        :param element: namedtuple('ELEMENT', ['name', 'css_selector'])
        :return: WebElement
        """
        return self.web_driver.find_element_by_css_selector(element.css_selector)

    def get_element_screenshot_to_bytes(self, ele):
        """
        获取指定元素截图的二进制字节
        :param ele: WebElement
        :return: Bytes
        """
        rect = ele.size
        loc = ele.location_once_scrolled_into_view
        time.sleep(4)
        left = loc['x']
        top = loc['y']
        right = left + rect['width']
        bottom = top + rect['height']
        box = (left, top, right, bottom)
        image = self.web_driver.get_screenshot_as_png()
        im = Image.open(io.BytesIO(image))
        ele_crop = im.crop(box)
        crop_im = io.BytesIO()
        ele_crop.save(crop_im, 'png')
        return crop_im.getvalue()

    def get_element_screenshot(self, ele, fp):
        """
        获取指定元素的截图并存储到相应文件
        :param ele: WebElement
        :param fp: file path
        :return: None
        """
        rect = ele.size
        loc = ele.location_once_scrolled_into_view
        time.sleep(4)
        left = loc['x']
        top = loc['y']
        right = left + rect['width']
        bottom = top + rect['height']
        box = (left, top, right, bottom)
        image = self.web_driver.get_screenshot_as_png()
        im = Image.open(io.BytesIO(image))
        ele_crop = im.crop(box)
        ele_crop.save(fp, 'png')

    def close(self):
        return self.web_driver.quit()


if __name__ == '__main__':
    # 测试代理
    chrome = Web(headless=False, proxy='180.120.207.252:29200')
    chrome.web_driver.get('https://www.httpbin.org/ip')
