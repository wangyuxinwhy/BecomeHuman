#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:51
# @Author  : yuxin.wang
# @File    : web_function_support.py
# @Project : BecomeHuman

from collections import namedtuple

PAGE = namedtuple('PAGE', ['name', 'url'])
BOOK = namedtuple('BOOk', ['name', 'id', 'description'])
PATTERN = namedtuple('PATTERN', ['name', 'pattern'])
ELEMENT = namedtuple('ELEMENT', ['name', 'css_selector'])

# DEFAULT
DEFAULT_BOOK = BOOK('弑神海', '755129', '修士一弹指，人间血花开！')
DEFAULT_BOOK_HOMEPAGE = PAGE('book_homepage', 'http://book.zongheng.com/book/755129.html')
DEFAULT_BOOK_CATALOGUE_PAGE = PAGE('catalogue_page', 'http://book.zongheng.com/showchapter/755129.html')
DEFAULT_BOOK_FIRST_CHAPTER = PAGE('first_chapter', 'http://book.zongheng.com/chapter/755129/41711093.html')


# book_name, author_name, recommend_book_name, book_description
COMMENT_LIST = ['{book_name}这本书写的真好，看了几章就被深深地吸引了，于是立马签到点赞。各位书友如果有空也可以看一看『{recommend_book_name}』--{book_description}',
                '前排支持{author_name}大大，『{recommend_book_name}』--{book_description}， 创作不易，希望大家支持！',
                '被{book_name}的文笔吸引，特来签到支持！，顺带携作品『{recommend_book_name}』前来拜访，望{author_name}大大回访、收藏、点评！！',
                '签到支持，看望{author_name}大大。{book_name}的书友们也请多多支持『{recommend_book_name}』--{book_description}']


# FUNCTION NEWS MEMBER TICKET COMMENT
FUNCTION_NEWS_MEMBER_TICKET_COMMENT_CONFIG = {
    'page': PAGE('NEWS_MEMBER_TICKET', 'http://news.zongheng.com/zhuanti/ypxxt/index.html'),
    'element': {'text_area': ELEMENT('text_area', '#leaveMessage'),
                'button': ELEMENT('button', 'body > div.bg > div.con > div.bot > div > div > div > form > input')},
    'comment': '《弑神海》 修士一弹指，人间血花开，求各位大大支持！'
}

# FUNCTION LOGIN
FUNCTION_LOGIN_CONFIG = {'page': {'login': PAGE('login_page', 'http://passport.zongheng.com/?location=http%3A%2F%2Fwww.zongheng.com%2Fcategory%2F1.html'),
                                  'homepage': PAGE('homepage', 'http://www.zongheng.com/')},
                         'element': {
                              'use_acpw': ELEMENT('login_use_acpw', 'body > div.passbg > div > div.login.box > div.login-style > span.login-s-user.fr'),
                              'username': ELEMENT('login_username', '#username'),
                              'password': ELEMENT('login_password', '#password'),
                              'code_input': ELEMENT('login_code_input', '#imgyzm2'),
                              'code_image': ELEMENT('login_code_image', 'body > div.passbg > div > div.login.box > div:nth-child(4) > p.error-more > img'),
                              'button': ELEMENT('login_click_button', 'body > div.passbg > div > div.login.box > div:nth-child(4) > input'),
                              'nick_name': ELEMENT('nickname', '#user_info > a.nickName')}}

# FUNCTION LOGIN WITH COOKIES
FUNCTION_LOGIN_WITH_COOKIES_CONFIG = {'page': PAGE('homepage', 'http://www.zongheng.com/'),
                                      'element': ELEMENT('nickname', '#user_info > a.nickName')}

# FUNCTION COLLECT BOOK
FUNCTION_COLLECT_BOOK_CONFIG = {'book_id': 755129,
                                'page_pattern': PATTERN('book_homepage', 'http://book.zongheng.com/book/{}.html'),
                                'element': {'collect': ELEMENT('collect', 'body > div:nth-child(4) > div > div.two_main.fl > div > div > div > div.status.fl > div.book_btn > span.btn_as.favorite > a'),
                                            'collect_ensure': ELEMENT('collect_ensure', '#ui_widget_message_dialog > div > div > input')}}

# FUNCTION READ BOOK WITH HISTORY
FUNCTION_READ_BOOK_WIYH_HISTORY_CONFIG = {'page': PAGE('first_chapter', 'http://book.zongheng.com/chapter/755129/41711093.html'),
                                          'element': {'next': ELEMENT('next_chapter', '#nextChapterButton')}}

# FUNCTION READ BOOK
FUNCTION_READ_BOOK_CONFIG = {'book_id': 755129,
                             'page_pattern': PATTERN('book_homepage', 'http://book.zongheng.com/book/{}.html'),
                             'element': {'read': ELEMENT('read', '#readRecord'),
                                         'next': ELEMENT('next_chapter', '#nextChapterButton')}}

# FUNCTION CHAPTER COMMENT
FUNCTION_CHAPTER_COMMENT_CONFIG = {'book_id': 755129,
                                   'chapter_id': 41711093,
                                   'page_pattern': PATTERN('book_chapter', 'http://book.zongheng.com/chapter/{}/{}.html'),
                                   'element': {'text_area': ELEMENT('chapter_comment_text_area', '#chapter_thread_panel > textarea'),
                                               'button': ELEMENT('chapter_comment_click', '#ui_send_chapter_thread_button'),
                                               'code_input': ELEMENT('chapter_comment_code_input', '#chapter_thread_panel > div.verifycode_panel > input.rep_titipt'),
                                               'code_image': ELEMENT('chapter_comment_code_image', '#chapter_thread_panel > div.verifycode_panel > img')},
                                   'comment': '《弑神海》 修士一弹指，人间血花开，求各位大大支持！'}

# # FUNCTION SEARCH BOOK
# FUNCTION_SEARCH_BOOK_CONFIG = {'page': PAGE('homepage', 'http://www.zongheng.com/'),
#                                'element': {'text_area': ELEMENT('search_text_area', '#\35 82455024 > span.input_text > input[type="text"]'),
#                                            'button': ELEMENT('search_button', '#\35 82455024 > input.sousuo')},
#                                'title': '弑神海'}

# FUNCTION ENTER USER HOME
FUNCTION_ENTER_USER_HOME_CONFIG = {'page': PAGE('homepage', 'http://home.zongheng.com/'),
                                   'element': {'nickname': ELEMENT('user_nick_name', '#bdbind > div.author_msg > div.au_head.clear > h3')}}

FUNCTION_BOOK_COMMENT_CONFIG = {'book_id': 755129,
                                'page_pattern': PATTERN('book_homepage', 'http://book.zongheng.com/book/{}.html'),
                                'element': {
                                    'title_text': ELEMENT('title_text', '#threadForm > table > tbody > tr:nth-child(1) > td:nth-child(2) > input[type="text"]'),
                                    'comment_text': ELEMENT('comment_text', '#threadForm > table > tbody > tr:nth-child(3) > td:nth-child(2) > textarea'),
                                    'code_input': ELEMENT('code_input', '#threadForm > table > tbody > tr.verifycode_panel > td.yzm > input[type="text"]'),
                                    'code_image': ELEMENT('code_input', '#threadForm > table > tbody > tr.verifycode_panel > td.yzm > img'),
                                    'button': ELEMENT('button', '#threadForm > table > tbody > tr:nth-child(5) > td.tr > input')
                                },
                                'title': '弑神海_前来拜访前辈',
                                'comment': '这本书写的真好，看了几章就被深深地吸引了，于是立马收藏点赞。各位书友如果有空也可以看一看『弑神海』--修士一弹指，人间血花开。 创作不易，希望大家支持！'}

# FUNCTION RECOMMEND
FUNCTION_BOOK_RECOMMEND_CONFIG = {'book_id': 755129,
                                  'page_pattern': PATTERN('book_homepage', 'http://book.zongheng.com/book/{}.html'),
                                  'element': {
                                      'button': ELEMENT('recommend_button', 'body > div:nth-child(4) > div > div.side > div > div.title > a > span'),
                                      'iframe': ELEMENT('recommend_iframe', '#ui_widget_dialog_frame'),
                                      'ensure': ELEMENT('recommend_ensure', '#recommendPanel > div.tc > input.submit.ensure')
                                  }}

# FUNCTION REGISTER
FUNCTION_REGISTER = {'page': 'http://passport.zongheng.com/webreg?location=http%3A%2F%2Fwww.zongheng.com%2F',
                     'element': {
                         'tel': ELEMENT('tel_input', '#regphone'),
                         'code_button': ELEMENT('send_code', 'body > div.reg-form > div:nth-child(2) > p:nth-child(3) > span'),
                         'code': ELEMENT('code_input', '#msgyzm'),
                         'button': ELEMENT('next', 'body > div.reg-form > div:nth-child(2) > div'),
                         'password': ELEMENT('password_input', '#regpassword'),
                         'ensure_password': ELEMENT('password_input_2', '#regpassword2'),
                         'button_2': ELEMENT('next_2', 'body > div.reg-form > div:nth-child(3) > div'),
                         'nickname': ELEMENT('nickname_input', '#regnickname')
                     }}
