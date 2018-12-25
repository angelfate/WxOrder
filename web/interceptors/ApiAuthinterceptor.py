__author__ = '未昔'
__date__ = '2018/11/26 14:51'
#拦截器
import re
from flask import request,jsonify,g

from application import app
from common.models.member.Member import Member
from common.libs.member.MemberService import MemberService
"""
    api小程序用户认证
"""

@app.before_request # 装饰器
def before_request():  # 请求之前的方法
    """
        功能：在每一个请求到底controller方法之前，都被这个方法拦截。
        思想：如果是请求登陆后的展示页面，通过 刚才设置的 cookie来验证。
    """
    api_ignore_urls = app.config['API_IGNORE_URLS']  # 哪些页面不登录也可以直接访问
    path = request.path   # 当前页面 url 地址
    if "/api" not in path:  # 如果请求没有api则不拦截
        return

    member_info = check_member_login()  # 调用下面check_login()的方法，判断小程序会员信息

    g.member_info = None
    if member_info: # 如果已经登录,就有 user_info
        g.member_info = member_info  #  g.current_user，就是当前用户信息

    # 拦截处理，加入日志（访问记录）
    pattern = re.compile('%s' % "|".join(api_ignore_urls)) # 如果是登录页面，则不拦截
    if pattern.match(path):
        return

    if not member_info: # 如果没有 member_info,则重新登录。小程序返回的是 json，不能再返回链接了
        resp = {'code':-1,'msg':'未登录','data':{}}
        return jsonify(resp)

    return


"""
判断用户是否已经登录
"""
def check_member_login():
    auth_cookie = request.headers.get("Authorization")   # 取出小程序会员的 头信息里面的这个授权码，进行验证

    if auth_cookie is None:
        return None

    auth_info = auth_cookie.split('#')
    if len(auth_info) !=2:
        return False  # 即为空

    try:
        member_info = Member.query.filter_by( id=auth_info[1] ).first()  # id 为 Authorization 加密后‘#’ 后面的部分
    except Exception:
        return False

    if member_info is None:  #如果拿到的加密信息(cookie值)里面的 uid，在数据库里面查不到这个user_info信息，说明这个uid是伪造的，uid为假
        return False

    if auth_info[0] != MemberService.geneAuthCode( member_info ):  # 如果uid为真，加密信息(cookie值)里面的 授权码部分 ！= 我们定义的授权码
        # 因为授权码，是通过数据库的uid对应数据生成的。但是，网页请求返回的授权码可能被篡改过
        return False

    if member_info.status != 1:
        return False

    return member_info  # 当 上面的全部为真时，则登陆成功

