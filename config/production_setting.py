__author__ = '未昔'
__date__ = '2018/11/21 19:05'
# 生产环境的配置

SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1/food_db'  # 数据库连接
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = "utf-8"
RELEASE_VERSION = '2018012041658001' # 版本号
