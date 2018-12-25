__author__ = '未昔'
__date__ = '2018/11/21 19:47'

"""
统一拦截器
"""
from web.interceptors.Authinterceptor import *
from web.interceptors.ApiAuthinterceptor import *
from web.interceptors.Errorinterceptor import *


"""
蓝图功能，对所有的URL进行蓝图功能配置
"""
from application import app
from web.controllers.index import route_index
from web.controllers.user.User import route_user
from web.controllers.static import route_static
from web.controllers.account.Account import route_account
from web.controllers.finance.Finance import route_finance
from web.controllers.food.Food import route_food
from web.controllers.member.Member import route_member
from web.controllers.stat.Stat import route_stat
from web.controllers.api import route_api
from web.controllers.upload.Upload import route_upload

app.config['JSON_AS_ASCII'] = False

app.register_blueprint( route_index, url_prefix="/")# 将路由注入进来
app.register_blueprint( route_user, url_prefix="/user")# 将路由注入进来

app.register_blueprint( route_static, url_prefix="/static") # 所有的route_static，前缀都是 static，都转移到static.py控制器下面统一处理
app.register_blueprint( route_account, url_prefix="/account") # root_account，前缀都是 account，都转移到Account.py控制器下面统一处理

app.register_blueprint( route_finance, url_prefix="/finance")
app.register_blueprint( route_food, url_prefix="/food")
app.register_blueprint( route_member, url_prefix="/member")  # 会员管理
app.register_blueprint( route_stat, url_prefix="/stat")

app.register_blueprint( route_api, url_prefix="/api")

app.register_blueprint( route_upload, url_prefix="/upload")
