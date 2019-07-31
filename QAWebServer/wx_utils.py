# -*- coding:utf-8 -*-
"""
Created on 2019/1/14 18:30
@author: Leo
@file:wx_utils.py
@desc:
"""
import datetime
import json
import logging
import threading
import time

import motor
import requests

from QUANTAXIS import QA_Portfolio, RUNNING_ENVIRONMENT, BROKER_TYPE, QA_Account, QA_User, DATABASE

from QAWebServer.config.setting import Setting

log=logging.getLogger(__name__)
base_url='https://api.weixin.qq.com/cgi-bin/'
wx_token=Setting().get('wx_token') or ''
wx_count=0
tousers=[Setting().get('tousers') or '']
lock = threading.Lock()

def wx_send_message(resource,message):
    if True:
        log.info('准备微信发送（生产模式）：%s %s', resource, message)
        headers = {
            'content-type': 'application/json'
        }
        url=base_url+resource+'?access_token='+wx_token
        if not isinstance(message,dict):
            message=json.loads(message)
        res = requests.post(url=url, json=message, headers=headers).json()
        # resp: {"errcode": 42001, "errmsg": "access_token expired hint: [vjp0438vr29!]"}
        if res.get('errcode') and res.get('errcode') in (42001,41001,40001):
            print('微信返回信息:',res)
            wx_update_token()
            wx_send_message(resource,message)
            # return
        else:
            print('微信返回信息：',res)
        # db_str={strategy_type:strategy_type,message_type:message_type,'timestamp':time.time(),'resource':resource,'message':message,'response':res}
        # log.info('微信发送内容：%s',db_str)
        # mongo_db.save(db_str, DB['t_wx_message'])
    else:
        log.info('微信发送（非生产模式）：%s %s %s %s',resource,message,strategy_type,message_type)

    pass
def wx_update_token():
    global wx_token,wx_time
    with lock:
        current_time=time.time()
        if current_time-wx_time<20:
            return
        else:
            log.info('准备更新token')
            url=Setting().get('wx_update_url') #测试号的url，不会变
            response = requests.post(url=url)
            res=response.json()
            if res.get('access_token'):

                wx_token=res.get('access_token')
                print(wx_token)
                Setting().saveOrUpdate('wx_token',wx_token)
                log.info('已更新token：%s' % wx_token)
                print('已更新token：%s' % wx_token)

                wx_time=time.time()
            else:
                log.critical('微信获取token出错!!! %s',res)

def send_message(mes_dict):
    code = str(mes_dict.get('code'))
    price = str(mes_dict.get('price'))
    amount = str(mes_dict.get('amount'))
    type = str(mes_dict.get('type'))
    status = str(mes_dict.get('status'))
    remark = str(mes_dict.get('remark'))
    print(datetime.datetime.now(),'准备启动发送微信...')
    thread = threading.Thread(target=wx_send_trade_message, args=(code,price,amount,type,status,remark))
    thread.start()

def wx_send_trade_message(code,price,amount,type,status,remark):

    template_id='Ft7dUDYvBbZnI25yeQ-NEEycxR2gGATIQh5WUAigHc0'
    '''
    股票代码：{{code.DATA}} 委托价格:{{price.DATA}} 委托数量:{{amount.DATA}} 方向:{{type.DATA}} 状态:{{status.DATA}} 说明:{{remark.DATA}}
    '''
    # code=str(mes_dict.get('code'))
    # price=str(mes_dict.get('price'))
    # amount=str(mes_dict.get('amount'))
    # type=str(mes_dict.get('type'))
    # status=str(mes_dict.get('status'))
    # remark=str(mes_dict.get('remark'))

    resource='message/template/send'
    for touser in tousers:
        message = {
            "touser": touser,
            "template_id": template_id,
            "url": "",
            "data": {
                "code": {
                    "value": code,
                    "color": "#173177"
                },
                "price": {
                    "value": price,
                    "color": "#173177"
                },
                "amount": {
                    "value": amount,
                    "color": "#173177"
                },
                "type": {
                    "value": type,
                    "color": "#FF2D2D"
                },
                "status": {
                    "value": status,
                    "color": "#FF2D2D"
                },
                "remark": {
                    "value": remark,
                    "color": "#173177"
                }
            }
        }
        wx_send_message(resource,message)

if __name__ == '__main__':
    # wx_update_token()
    # print(wx_token)
    # print(load_config())

    print(wx_token)
    mes_dict={'code':'002027','price':6.95392,'amount':200,'type':'buy','status':'未报','remark':'2019-02-27 22:13 close_price=2.7'}
    '''
    2019-02-27 09:31:19.966344 返回交易信号: {'trade': 'grid', 'buy_price': 6.95392, 'sell_price': 7.02402, 'open': 7.01, 'last_close': 6.89, 'type': 'open>last_close*1.01'}
    '''
    send_message(mes_dict)
    time.sleep(10)
    # with open(wx_file, "w", encoding="utf-8") as f:
    #     pass
    #     # yaml.dump('token': 'ddddddddddddddd', f)