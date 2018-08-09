#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:49
# @Author  : yuxin.wang
# @File    : web_function.py
# @Project : BecomeHuman

import time
import random
from logging import getLogger

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import NOVEL_READ_TIME, NOVEL_MAX_READ_CHAPTER
from config import WEBFUNC_DEFAULT_RETRY_TIMES
from exceptions import ContextError
from database import get_user_action_collections, get_user_collections
from zongheng.check import *
from zongheng.web_function_support import *
from zongheng.api import api_book_comment, api_book_chapter_comment
from zongheng.check import get_exception_info_from_checklist
from helper.identify_code import identify_code_from_url, identify_code_from_bytes
from helper.utils import get_phone_num, get_phone_message, get_register_info


logger = getLogger('general')


class WebFunction:

    def __init__(self, web, user=None, config=None):
        self.web = web
        self.user = user
        self.checklist = []
        self.info = {
            'user': self.user.nickname if user else 'No user',
            'username': self.user.nickname if user else 'No user',
            'action': self.__class__.__name__,
            'status': None,
            'start_time': None,
            'end_time': None,
            'info': {}
        }
        self.config = config

    def concrete_run(self):
        """运作方法, 返回True or False"""
        pass

    def check_context(self):
        """
        检查功能执行所需的上下文环境
        :return:  Bool
        """

        if not self.checklist:
            return True
        else:
            checklist_status = [0] * len(self.checklist)
            checklist_instance = [check(self.web, self.user) for check in self.checklist]
            checklist_description = [check.description for check in checklist_instance]

            for index, c in enumerate(checklist_instance):
                if c.check():
                    checklist_status[index] = 1

            if all(checklist_status):
                return True
            else:
                info = get_exception_info_from_checklist(checklist_status, checklist_description)
                raise ContextError('{} Context: {}'.format(self.__class__, info))

    def function_success(self):
        """功能运作成功"""
        pass

    def function_failed(self):
        """功能运作失败"""
        self.retry()

    def is_success(self):
        """是否成功的判断"""
        return True

    def run(self):

        start_time = int(time.time())
        self.info['start_time'] = start_time
        if self.check_context():
            logger.info('{}|{}: {}'.format(self.__class__.__name__, 'check_context', 'SUCCESS'))
            logger.info('{}|{}: {}'.format(self.__class__.__name__, 'concrete_run', 'RUNNING'))
            self.concrete_run()
            time.sleep(2)
            try:
                success = self.is_success()
                if success:
                    logger.info('{}|{}: {}'.format(self.__class__.__name__, 'concrete_run', 'SUCCESS'))
                    self.info['status'] = 1
                    self.function_success()
                else:
                    raise Exception('{} Error'.format(self.__class__.__name__))
            except Exception as e:
                # self.web.web_driver.save_screenshot('screen_{}.png'.format(time.time()))
                logger.error('{}|{} -> {}'.format(self.__class__.__name__, 'FAILED', e))
                self.info['status'] = 0
                self.function_failed()
        end_time = int(time.time())
        self.info['end_time'] = end_time
        user_action_col = get_user_action_collections()
        user_action_col.insert(self.info)

    def retry(self, times=WEBFUNC_DEFAULT_RETRY_TIMES):
        retry_times_count = 0
        while retry_times_count < times:
            retry_times_count += 1
            logger.info(
                '{}|{}: {} {} times'.format(self.__class__.__name__, 'concrete_run', 'RETRY', retry_times_count))
            self.concrete_run()
            try:
                if self.is_success():
                    self.function_success()
                    self.info['status'] = 1
                    logger.info('{}|{}: {}'.format(self.__class__.__name__, 'concrete_run', 'SUCCESS'))
                    break
                else:
                    raise Exception('检验操作未成功')
            except Exception as e:
                logger.error('{}|{}: {} --> {}'.format(self.__class__.__name__, 'concrete_run', 'FAILED', e))


class Login(WebFunction):
    """
    通过模拟登录，从目标网站登录页开始
    """

    def __init__(self, web, user, config=FUNCTION_LOGIN_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckUserName, CheckPassword, CheckWebDriver]

    def concrete_run(self):
        # 登录准备
        self.user.work_times = int(self.user.work_times) + 1
        self.user.last_work_time = int(time.time())

        # 模拟登录
        self.web.web_driver.get(self.config['page']['login'].url)
        time.sleep(3)

        ac_pw_ele = self.web.get_element(self.config['element']['use_acpw'])
        ac_pw_ele.click()

        input_ac_ele = self.web.get_element(self.config['element']['username'])
        input_pw_ele = self.web.get_element(self.config['element']['password'])
        login_bt_ele = self.web.get_element(self.config['element']['button'])

        input_ac_ele.send_keys(self.user.username)
        input_pw_ele.send_keys(self.user.password)
        time.sleep(2)
        id_pic = self.web.get_element(self.config['element']['code_image'])
        WebDriverWait(self.web.web_driver, 20).until(EC.visibility_of(id_pic))
        input_id_pic = self.web.get_element(self.config['element']['code_input'])

        pic_url = id_pic.get_attribute('src')
        code = identify_code_from_url(pic_url)
        input_id_pic.send_keys(code)
        login_bt_ele.click()
        time.sleep(2)
        self.web.web_driver.get(self.config['page']['homepage'].url)

    def is_success(self):
        web_page_show_user_nickname = self.web.get_element(self.config['element']['nick_name']).text
        if self.user.nickname[:3] == web_page_show_user_nickname[:3]:
            return True

    def function_success(self):
        self.web.is_login = True
        self.user.cookies = self.web.web_driver.get_cookies()
        self.user.is_last_work_success = 1

    def function_failed(self):
        self.user.is_last_work_success = 0
        self.user.work_failed_times = int(self.user.work_failed_times) + 1
        self.retry()


class LoginWithCookies(WebFunction):
    """
    通过添加Cookies，登录目标网站主页
    """

    def __init__(self, web, user, config=FUNCTION_LOGIN_WITH_COOKIES_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckWebDriver, CheckCookies]

    def concrete_run(self):

        # 登录准备
        self.user.work_times = int(self.user.work_times) + 1
        self.user.last_work_time = int(time.time())

        # 模拟登录
        self.web.web_driver.get(self.config['page'].url)
        for c in self.user.cookies:
            self.web.web_driver.add_cookie(c)
        self.web.web_driver.refresh()

    def is_success(self):
        try:
            web_page_show_user_nickname = self.web.get_element(self.config['element'])
            WebDriverWait(self.web.web_driver, 20).until(EC.visibility_of(web_page_show_user_nickname))
            text = web_page_show_user_nickname.text
            if self.user.nickname[:3] == text[:3]:
                return True
        except Exception:
            return False

    def function_success(self):
        self.web.is_login = True
        self.user.is_last_work_success = 1

    def function_failed(self):
        self.user.is_last_work_success = 0
        self.user.work_failed_times = int(self.user.work_failed_times) + 1
        self.retry(1)


class CollectBook(WebFunction):

    def __init__(self, web, user, config=FUNCTION_COLLECT_BOOK_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):

        self.web.web_driver.get(self.config['page_pattern'].pattern.format(self.config['book_id']))
        button_collect = self.web.get_element(self.config['element']['collect'])
        time.sleep(3)
        button_collect.click()
        button_ensure = self.web.get_element(self.config['element']['collect_ensure'])
        button_ensure.click()

    def is_success(self):
        b = self.web.get_element(self.config['element']['collect'])
        if b.text == '已收藏':
            return True

    def function_success(self):
        self.user.is_collect = 1
        self.info['info']['collect_book_id'] = self.config['book_id']

    def function_failed(self):
        self.retry()


class ReadBook(WebFunction):

    def __init__(self, web, user, config=FUNCTION_READ_BOOK_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):

        self.web.web_driver.get(self.config['page_pattern'].pattern.format(self.config['book_id']))
        read_button = self.web.get_element(self.config['element']['read'])
        read_button.click()

        read_chapter_count = 0
        last_page_url = ''
        self.info['info']['start_url'] = self.web.web_driver.current_url
        while self.web.web_driver.current_url != last_page_url and read_chapter_count <= NOVEL_MAX_READ_CHAPTER:
            last_page_url = self.web.web_driver.current_url
            button_next_chapter = self.web.get_element(self.config['element']['next'])
            self.web.web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});",
                                               button_next_chapter)
            time.sleep(NOVEL_READ_TIME)
            logger.info('{}|{} reading {}'.format(self.__class__.__name__,
                                                  self.user.nickname, last_page_url))
            button_next_chapter.click()
            time.sleep(1)
            read_chapter_count += 1
            self.user.last_chapter_url = self.web.web_driver.current_url
        self.info['info']['end_url'] = self.web.web_driver.current_url


class ReadBookWithHistory(WebFunction):

    def __init__(self, web, user, config=FUNCTION_READ_BOOK_WIYH_HISTORY_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):

        if self.user.last_chapter_url:
            url = self.user.last_chapter_url
        else:
            url = self.config['page'].url

        self.web.web_driver.get(url)
        read_chapter_count = 0
        last_page_url = ''
        self.info['info']['start_url'] = self.web.web_driver.current_url
        while self.web.web_driver.current_url != last_page_url and read_chapter_count <= NOVEL_MAX_READ_CHAPTER:
            last_page_url = self.web.web_driver.current_url
            button_next_chapter = self.web.get_element(self.config['element']['next'])
            self.web.web_driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});",
                                               button_next_chapter)
            time.sleep(NOVEL_READ_TIME)
            button_next_chapter.click()
            time.sleep(1)
            read_chapter_count += 1
            self.user.last_chapter_url = self.web.web_driver.current_url
        self.info['info']['end_url'] = self.web.web_driver.current_url


class ChapterComment(WebFunction):

    def __init__(self, web, user, config=FUNCTION_CHAPTER_COMMENT_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):

        self.info['info']['book_id'] = self.config['book_id']
        self.info['info']['chapter_id'] = self.config['chapter_id']
        self.info['info']['comment'] = self.config['comment']
        url = self.config['page_pattern'].pattern.format(self.config['book_id'], self.config['chapter_id'])
        self.web.web_driver.get(url)
        textarea = self.web.get_element(self.config['element']['text_area'])
        time.sleep(2)
        textarea.send_keys(self.config['comment'])
        time.sleep(5)
        code_input = self.web.get_element(self.config['element']['code_input'])
        code_image = self.web.get_element(self.config['element']['code_image'])
        button = self.web.get_element(self.config['element']['button'])
        im = self.web.get_element_screenshot_to_bytes(code_image)
        time.sleep(1)
        code = identify_code_from_bytes(im)
        code_input.send_keys(code)
        button.click()
        logger.info('{} | {} comment {}'.format(self.__class__.__name__, self.user.nickname, url))

    def is_success(self):
        comment_list = api_book_chapter_comment(self.config['book_id'], self.config['chapter_id'])['threadViewList']
        for i in comment_list:
            if i['userName'] in self.user.nickname:
                return True

    def function_failed(self):
        pass


class BookComment(WebFunction):

    def __init__(self, web, user, config=FUNCTION_BOOK_COMMENT_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):
        self.info['info']['book_id'] = self.config['book_id']
        self.info['info']['title'] = self.config['title']
        self.info['info']['comment'] = self.config['comment']
        url = self.config['page_pattern'].pattern.format(self.config['book_id'])
        self.web.web_driver.get(url)
        title = self.web.get_element(self.config['element']['title_text'])
        comment = self.web.get_element(self.config['element']['comment_text'])
        title.send_keys(self.config['title'])
        comment.send_keys(self.config['comment'])
        code_input = self.web.get_element(self.config['element']['code_input'])
        code_image = self.web.get_element(self.config['element']['code_image'])
        button = self.web.get_element(self.config['element']['button'])
        time.sleep(1)
        im = self.web.get_element_screenshot_to_bytes(code_image)
        code = identify_code_from_bytes(im)
        code_input.send_keys(code)
        button.click()
        time.sleep(0.5)
        logger.info('{} | {} comment {}'.format(self.__class__.__name__, self.user.nickname, url))

    def is_success(self):
        content = api_book_comment(self.config['book_id'])
        return self.user.nickname in content

    def function_failed(self):
        pass


class RecommendBook(WebFunction):

    def __init__(self, web, user, config=FUNCTION_BOOK_RECOMMEND_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin, CheckCookies, CheckCommend]

    def concrete_run(self):
        self.web.web_driver.get(self.config['page_pattern'].pattern.format(self.config['book_id']))
        button = self.web.get_element(self.config['element']['button'])
        button.click()
        iframe = self.web.get_element(self.config['element']['iframe'])
        self.web.web_driver.switch_to.frame(iframe)
        ensure = self.web.get_element(self.config['element']['ensure'])
        ensure.click()
        self.info['info']['book_id'] = self.config['book_id']


class NewsMemberTicketComment(WebFunction):

    def __init__(self, web, user, config=FUNCTION_NEWS_MEMBER_TICKET_COMMENT_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):
        self.web.web_driver.get(self.config['page'].url)
        text_area = self.web.get_element(self.config['element']['text_area'])
        button = self.web.get_element(self.config['element']['button'])
        text_area.send_keys(self.config['comment'])
        button.click()


class EnterUserHome(WebFunction):

    def __init__(self, web, user, config=FUNCTION_NEWS_MEMBER_TICKET_COMMENT_CONFIG):
        super().__init__(web, user, config)
        self.checklist = [CheckLogin]

    def concrete_run(self):
        self.web.web_driver.get(self.config['page'].url)

    def is_success(self):
        nickname_ele = self.web.get_element(self.config['element']['nickname'])
        nickname = nickname_ele.text
        if self.user.nickname == nickname:
            return True


class Register(WebFunction):

    def __init__(self, web, config=FUNCTION_REGISTER):
        super().__init__(web, config=config)
        self.phone_num = get_phone_num()
        self.password, self.nickname = get_register_info(self.phone_num)

    def concrete_run(self):
        self.phone_num = get_phone_num()
        self.web.web_driver.get(self.config['page'])
        tel = self.web.get_element(self.config['element']['tel'])
        tel.send_keys(self.phone_num)
        time.sleep(.5)
        send_code = self.web.get_element(self.config['element']['code_button'])
        code_input = self.web.get_element(self.config['element']['code'])
        button = self.web.get_element(self.config['element']['button'])
        send_code.click()
        code = get_phone_message(self.phone_num)
        code_input.send_keys(code)
        time.sleep(.5)
        button.click()
        self.password, self.nickname = get_register_info(self.phone_num)
        password_input_1 = self.web.get_element(self.config['element']['password'])
        password_input_2 = self.web.get_element(self.config['element']['ensure_password'])
        nickname_input = self.web.get_element(self.config['element']['nickname'])
        button_2 = self.web.get_element(self.config['element']['button_2'])
        password_input_1.send_keys(self.password)
        time.sleep(.5)
        password_input_2.send_keys(self.password)
        time.sleep(.5)
        nickname_input.send_keys(self.nickname)
        button_2.click()

    def is_success(self):
        success = ELEMENT('is_success', 'body > div.reg-form > div.reg-step.last-step > p')
        text = self.web.get_element(success).text
        count = 0
        if count > 1:
            return False

        if '成功' not in text:
            count += 1
            suffix = random.randint(1, 20)
            self.nickname = self.nickname + str(suffix)
            nickname_input = self.web.get_element(self.config['element']['nickname'])
            nickname_input.clear()
            nickname_input.send_keys(self.nickname)
            button_2 = self.web.get_element(self.config['element']['button_2'])
            button_2.click()
            time.sleep(3)
            if self.is_success():
                return True
            else:
                raise Exception('昵称错误')
        else:
            return True

    def function_failed(self):
        pass

    def function_success(self):
        self.info['info']['username'] = self.phone_num
        self.info['info']['password'] = self.password
        self.info['info']['nickname'] = self.nickname
        user_info = {
            'username': self.phone_num,
            'password': self.password,
            'nickname': self.nickname
        }
        user_col = get_user_collections()
        user_col.insert(user_info)


if __name__ == '__main__':
    pass
