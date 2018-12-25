    # -*- coding: utf-8 -*-
import time

from application import app  # 设置开发时，js版本可以一直变化，不用刷新。发布时，不变

class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        release_version = app.config.get('RELEASE_VERSION')
        ver = "%s"%(int(time.time())) if not release_version else release_version  # 如果没有release_version时，就是时间戳，否则 就是定义的版本号
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    @staticmethod
    def buildImageUrl(path):
        ## 上传的图片 的url静态拼接方法
        app_config = app.config['APP']  # 图片域名，进行统一封装
        url = app_config['domain'] + app.config['UPLOAD']['prefix_url'] + path
        return url  # 返回的是绝对地址。域名+图片前缀+key

