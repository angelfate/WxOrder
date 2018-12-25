__author__ = '未昔'
__date__ = '2018/11/21 19:04'
#本地开发环境配置demo
DEBUG = True
SQLALCHEMY_ECHO = True  # 打印所有sql语句
SERVER_PORT = 8999  # 运行端口
SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1/food_db'  # 数据库连接
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf-8"
