__author__ = '未昔'
__date__ = '2018/11/22 12:20'

from flask import Blueprint,g

from common.libs.Helper import ops_render


route_index = Blueprint( 'index_page',__name__ )  # 入口文件


@route_index.route("/")
def index():
    #获取用户当前的登录状态
    return ops_render("index/index.html")  # 后端逻辑传回前端页面
