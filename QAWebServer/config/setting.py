# -*- coding:utf-8 -*-
"""
Created on 2019/1/16 14:28
@author: Leo
@file:otsetting.py
@desc:
"""
import logging
import pymongo
import time

import motor
from QUANTAXIS.QAUtil import singleton
from QUANTAXIS.QAUtil.QASetting import MJK_DATABASE
from cacheout import Cache


log = logging.getLogger(__name__)
@singleton
class Setting():
    __tablename__='setting'

    def __init__(self):
        self._cache=Cache(ttl=30)
        self._collection=MJK_DATABASE[self.__tablename__]
        # try:
        #     self._collection=ConfigData().db[self.__tablename__]
        # except:
        #     config_file = 'config.yaml'
        #     config = load_config(config_file)
        #     ConfigData().init(config)
        #
        #     client = pymongo.MongoClient(config["database"]["config"])
        #     database = client[config["database"]["db"]]
        #     ConfigData().set_db(database)
        #     self._collection = ConfigData().db[self.__tablename__]
        pass
    def update(self,key,value,remark=None):
        result=self._update_one(key,value,remark)
        if result.modified_count==1:
            log.critical('%s数据更新成功%s', key,value)
            res = self._find_one(key)
            if value:
                self._cache.set(key, res)
        else:
            log.critical('找不到%s的数据', key)

    def saveOrUpdate(self,key,value,dataype='str',defaultvalue='',remark=None):
        result = self._update_one(key, value,remark,dataype,defaultvalue,upsert=True)
        if result.modified_count == 1:
            log.critical('%s数据更新成功%s', key, value)
            res = self._find_one(key)
            if value:
                self._cache.set(key, res)
        else:
            log.critical('找不到%s的数据', key)
    def save(self,key,value,remark=None):
        v=self._find_one(key)
        if v:
            log.critical('%s 的数据已经存在，不允许insert %s',key,value)
        else:
            self.saveOrUpdate(key,value,remark)
    def get(self,key,datatype=str,default='',ttl=30):
        try:
            value = self._cache.get(key)
            if not value:
                value=self._find_one(key)
                if value:
                    self._cache.set(key,value,ttl=ttl)
                else:
                    log.critical('找不到%s的数据',key)
            t_dt=value.get('datatype')
            if t_dt=='int':
                datatype=int
            elif t_dt=='float':
                datatype=float
            elif t_dt=='str':
                datatype=str
            elif t_dt=='dict':
                datatype=dict
            elif t_dt=='tuple':
                datatype=tuple
            elif t_dt=='list':
                datatype=list
            default=value.get('defaultvalue') or default
            return datatype(value.get('value')) if value else default
        except Exception as e:
            log.critical('读取配置出错 %s %s',key,repr(e))
            return default

    def getObject(self,key):
        value = self._cache.get(key)
        if not value:
            value=self._find_one(key)
            if value:
                self._cache.set(key,value)
            else:
                log.critical('找不到%s的数据',key)
        return value

    def _find_one(self,key):
        return self._collection.find_one({'key': key})
    def _update_one(self,key,value,remark=None,datatype=str,defaultValue='',upsert=False):
        return self._collection.update_one({'key':key},{'$set':{'value':value,'updatetime':time.time(),'remark':remark,'datatype':datatype,'defaultvalue':defaultValue}},upsert=upsert)


