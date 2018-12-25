__author__ = '未昔'
__date__ = '2018/12/4 17:26'
from flask import request,g
import json

from application import app,db
from common.models.log.AppAccessLog import AppAccessLog
from common.models.log.AppErrorLog import AppErrorLog
from common.libs.Helper import getCurrentData


class LogService():

    @staticmethod  # 静态方法
    def addAccessLog():
        """
            访问记录
        """
        target = AppAccessLog()
        target.target_url = request.url  # 请求的链接
        target.referer_url = request.referrer
        target.ip = request.remote_addr  # 远程地址
        target.query_params = json.dumps( request.values.to_dict() ) # 使用json的方式传进来。dumps将字符串解析成json。to_dict()：请求的数据转化成字典
        if 'current_user' in g and g.current_user is not None:
            target.uid = g.current_user.uid
        target.ua = request.headers.get( "User-Agent" ) # 用户头信息
        target.created_time = getCurrentData()

        db.session.add( target )
        db.session.commit()
        return True


    @staticmethod
    def addErrorLog( content ): # content 是错误拦截器传回的e
        """
            错误记录
        """
        target = AppErrorLog()
        target.target_url = request.url  # 请求的链接
        target.referer_url = request.referrer
        target.ip = request.remote_addr  # 远程地址
        target.query_params = json.dumps(request.values.to_dict())  # 使用json的方式传进来。dumps将字符串解析成json。to_dict()：请求的数据转化成字典
        target.content = content
        target.created_time = getCurrentData()

        db.session.add(target)
        db.session.commit()
        return True
