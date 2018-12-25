__author__ = '未昔'
__date__ = '2018/11/21 19:46'

from flask import Flask
from flask_script import Manager # 对app进行包装
from flask_sqlalchemy import SQLAlchemy
import os


class Application( Flask ): # 实现配置按需加载分离，定义类，继承flask
    def __init__(self,import_name, template_folder=None, root_path=None):  # temlate_folder 重写模版路径
        super( Application,self).__init__( import_name,template_folder = template_folder,root_path=root_path,static_folder=None)  # 继承父类
        self.config.from_pyfile( 'config/base_setting.py',)  # 定义配置文件，从py文件加载
        self.config.from_pyfile('config/local_setting_demo.py')  # 定义配置文件，从py文件加载
        if "ops_config" in os.environ:
            self.config.from_pyfile('config/%s_setting.py'%os.environ['ops_config'])

        db.init_app( self)  # db重新初始化变量app


db = SQLAlchemy( )
app = Application( __name__,template_folder=os.getcwd()+"/web/templates/")
manager = Manager( app )



"""
函数模版
"""
from common.libs.UrlManager import UrlManager
app.add_template_global( UrlManager.buildStaticUrl,'buildStaticUrl')  # 将 静态方法注入进来
app.add_template_global( UrlManager.buildUrl,'buildUrl')  # 把这两个方法放到模版里面使用
app.add_template_global( UrlManager.buildImageUrl,'buildImageUrl')  # 把buildImageUrl报漏出来。10-8，15:20

