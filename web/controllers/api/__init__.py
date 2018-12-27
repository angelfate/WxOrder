__author__ = '未昔'
__date__ = '2018/12/5 18:49'
from flask import Blueprint

route_api = Blueprint( 'api_page',__name__ )  #定义标识
# 代码顺序，下面的要放在，标识后面
from web.controllers.api.Member import * # 作业就可以将 Member里面的代码，全部放到 init里面，然后在www里面就可以被注册了
from web.controllers.api.Food import * # 将 代码注册进来
from web.controllers.api.Cart import * # 将 代码注册进来
from web.controllers.api.Order import * # 将 代码注册进来


@route_api.route("/") # / 默认访问 index页面
def index():
    return "Mina Api V1.0"


