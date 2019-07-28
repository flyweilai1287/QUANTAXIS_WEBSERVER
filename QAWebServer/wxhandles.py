# -*- coding:utf-8 -*-
"""
Created on 2019/7/28 13:47
@author: Leo
@file:wxhandles.py.py
@desc:
"""
from QAWebServer.basehandles import QABaseHandler
from QAWebServer.wx_utils import send_message


class WxSendHandler(QABaseHandler):

    def post(self):
        openid = self.get_body_argument('openid', default="")
        content = self.get_body_argument('content', default="")
        try:
            content = eval(content)
        except:
            raise
        send_message(content)
        result={'result':'SUCCESS'}
        self.write(result)

