__author__ = '未昔'
__date__ = '2018/11/26 14:51'
#拦截器
import re
from flask import request,redirect,g

from application import app
from common.models.user import User
from common.libs.user.UserService import UserService
from common.libs.UrlManager import UrlManager
from common.libs.LogService import LogService


@app.before_request # 装饰器
def before_request():  # 请求之前的方法
    """
        功能：在每一个请求到底controller方法之前，都被这个方法拦截。
        思想：如果是请求登陆后的展示页面，通过 刚才设置的 cookie来验证。
    """
    ignore_urls = app.config['IGNORE_URLS']
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
    path = request.path   # 当前页面 url 地址

    # 通过正则表达式来判断
    pattern = re.compile( '%s' % "|".join( ignore_check_login_urls ))  # 如果当前路径有这个，则不拦截
    if pattern.match(path):
        return

    if "/api" in path:  # 如果请求的地址有 api，就不进行拦截。拦截主要是针对后端admin
        return

    user_info = check_login()  # 调用下面check_login()的方法

    g.current_user = None
    if user_info: # 如果已经登录,就有 user_info
        g.current_user = user_info  #  g.current_user，就是当前用户信息

    ## 拦截处理，加入日志（访问记录）
    LogService.addAccessLog() # 这里不需要任何参数，自定义的方法里面可以通过方式自己获取
    pattern = re.compile('%s' % "|".join(ignore_urls)) # 如果是登录页面，则不拦截
    if pattern.match(path):
        return

    if not user_info: # 如果没有 user_info,则重新登录
        return redirect( UrlManager.buildUrl( "/user/login" ))
    return


"""
判断用户是否已经登录
"""
def check_login():
    cookies = request.cookies  # 拿到 cookie
    auth_cookie = cookies[ app.config['AUTH_COOKIE_NAME'] ] if app.config['AUTH_COOKIE_NAME'] in cookies else None # 三连表达式。值如果在里面，否则

    # cookie 对比。从cookie取出 uid，通过uid从数据库查出个人信息，通过个人信息生成授权码。和cookie的授权码进行对比，两个如果不一致，则被更改，重新登录。
    if auth_cookie is None:
        return None

    auth_info = auth_cookie.split('#')
    if len(auth_info) !=2:
        return False  # 即为空

    try:
        user_info = User.query.filter_by( uid=auth_info[1] ).first()  # uid 为 cookies 加密后‘#’ 后面的部分
    except Exception:
        return False

    if user_info is None:  #如果拿到的加密信息(cookie值)里面的 uid，在数据库里面查不到这个user_info信息，说明这个uid是伪造的，uid为假
        return False

    if auth_info[0] != UserService.geneAuthCode( user_info ):  # 如果uid为真，加密信息(cookie值)里面的 授权码部分 ！= 我们定义的授权码
        # 因为授权码，是通过数据库的uid对应数据生成的。但是，网页请求返回的授权码可能被篡改过
        return False

    if user_info.status != 1:
        return False

    return user_info  # 当 上面的全部为真时，则登陆成功

