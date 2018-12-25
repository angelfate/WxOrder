__author__ = '未昔'
__date__ = '2018/11/22 17:13'

from flask import Blueprint,request,jsonify,make_response,redirect,g
import json  # dump 返回json序列化
import re

from common.models.user import (User)
from common.models.user_ip import (UserIp)
from common.libs.user.UserService import (UserService)
from common.libs.Helper import (ops_render)
from common.libs.UrlManager import (UrlManager)
from common.libs.forms import REGEX_Email,REGEX_MOBILE
from application import app,db



route_user = Blueprint( 'user_page',__name__ )



@route_user.route("/login",methods = ["GET","POST"]) # methods:传入post方法
def login():
    """
        登录页面，后台逻辑
    """
    if request.method == "GET":  # get请求
        return ops_render( "user/login.html")

    # 获取登录变量
    resp = { 'code':200,'msg':u"登陆成功",'data':{} } # 返回的信息用json值。定义整体全局变量 resp,即默认状态，data格外扩展字段

    req = request.values  # 所有的请求变量，放到这个数组里
    login_name = req['login_name'] if 'login_name' in req else ''  # 请求的变量 login_name 如果它在 请求里面，没有就是空
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''  # 请求的变量 login_name 如果它在 请求里面，没有就是空

    if login_name is None or len(login_name)<2:  # 判断账号长度
        resp['code'] = -1   # 返回的状态码
        resp['msg'] = u"请输入正确的用户登录名"  # 返回的信息
        # return json.dumps( resp,ensure_ascii=False )  # 用 jsonify 把json返回回去
        return jsonify(resp) # 用 jsonify 把json返回回去

    if login_pwd is None or len(login_pwd) < 6:
        resp['code'] = -1
        resp['msg'] = u"请输入正确的用户登录名和密码1"
        return jsonify( resp )

    user_info = User.query.filter_by( login_name=login_name ).first()  # User表中查询 请求的login_name 与表中对应的第一个。因为用户名是唯一的
    if not user_info:  # 如果用户名不在user里面
        resp['code'] = -1
        resp['msg'] = u"请输入正确的用户登录名和密码3"  # 返回的信息。返回两个是防止有人试登录信息
        return jsonify(resp)

    if  user_info.status != 1 :
        resp['code'] = -1
        resp['msg'] = u"账号已被禁用，请联系管理员Q：1040691703"
        return jsonify(resp)

    if user_info.login_pwd != UserService.genePwd( login_pwd,user_info.login_salt ): # 如果数据库查询到的用户密码 != 生成的密码（login_salt：登录秘钥）
        resp['code'] = -1
        resp['msg'] = u"请输入正确的用户登录名和密码4"
        return jsonify(resp)

    response = make_response( json.dumps( resp ) ) #返回dumps:json序列化
    response.set_cookie( app.config['AUTH_COOKIE_NAME'],"%s#%s"%( UserService.geneAuthCode( user_info ),user_info.uid ),60*60*24*7) # 设置cookie。cookie名称yl_food。cookie值 %s#%s。第一个%s为加密,后面的东西为用户uid明文。cookie保存7天

    return response


@route_user.route("/edit",methods = ["GET","POST"])  # 加装饰器，方法名叫 edit
def edit():
    """
        修改信息页面后台逻辑
    """
    if request.method == "GET":
        return ops_render( "user/edit.html",{ "current":"edit" })

    resp = {'code': 200, 'msg': u"操作成功", 'data': {}}
    # 获取登录变量
    req = request.values  # 所有的请求变量，放到这个数组里
    nickname = req['nickname'] if 'nickname' in req else ''  # 三元表达式
    email = req['email'] if 'email' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''

    if nickname is None or len(nickname)<2:# 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify(resp)  # json 格式的转换

    # if email is None or len(email)<6 or '@' not in email or '.' not in email:# 进行参数判断
    if not re.match(REGEX_Email,email):
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱"
        return jsonify(resp)  # json 格式的转换

    if not re.match(REGEX_MOBILE,mobile):
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的手机号"
        return jsonify(resp)  # json 格式的转换


    user_info = g.current_user  # 获得当前的用户信息
    user_info.nickname = nickname  # 更新 nickname
    user_info.email = email        # 更新 email
    user_info.mobile = mobile  # 更新 email

    db.session.add( user_info )  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功


@route_user.route("/reset-pwd",methods = ["GET","POST"])  # 加装饰器，方法名叫 reset-pwd
def resetPwd():
    """
        修改密码后台逻辑
    """
    if request.method == "GET":
        return ops_render( "user/reset_pwd.html",{ "current":"reset-pwd"} )

    resp = {'code': 200, 'msg': u"密码修改成功", 'data': {}}
    # 获取登录变量
    req = request.values  # 所有的请求变量，放到这个数组里
    old_password = req['old_password'] if 'old_password' in req else ''  # 参数有效性判断
    new_password = req['new_password'] if 'new_password' in req else ''
    # new_password2 = req['new_password2'] if 'new_password2' in req else ''  # 为什么拿不到这个数据？？？

    if old_password is None or len(old_password)<6:
        resp['code'] = -1
        resp['msg'] = "请输入不少于6位的原始密码"
        return jsonify(resp)

    if new_password is None or len(new_password) < 6:
        resp['code'] = -1
        resp['msg'] = "请输入不少于6位的新密码"
        return jsonify(resp)

    if len(new_password) > 15:
        resp['code'] = -1
        resp['msg'] = "请输入不超过15位的新密码"
        return jsonify(resp)

    if old_password == new_password:
        resp['code'] = -1
        resp['msg'] = "新密码与原密码不能相同"
        return jsonify(resp)

    # if new_password2 != new_password:
    #     print(new_password,'awd',new_password2)
    #     resp['code'] = -1
    #     resp['msg'] = "两次密码不一致"
    #     return jsonify(resp)

    user_info = g.current_user  # 得到改密的用户信息
    if user_info.login_pwd != UserService.genePwd( old_password,user_info.login_salt ): # User表中查询 请求的login_name 与表中对应的第一个。因为用户名是唯一的
        # 如果数据库查询到的用户密码 != 由用户输入的旧密码所生成的密码（login_salt：登录秘钥）
        resp['code'] = -1
        resp['msg'] = u"原密码错误"
        return jsonify(resp)

    user_info.login_pwd = UserService.genePwd( new_password,user_info.login_salt )   # 存的是加密后的密码

    db.session.add(user_info)  # 数据库添加数据，统一提交
    db.session.commit()

    # 更新cookie，密码修改完后，cookie值就变量
    response = make_response(json.dumps(resp))  # 返回dumps:json序列化
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], "%s#%s" % (UserService.geneAuthCode(user_info), user_info.uid),
                        60 * 60 * 24 * 7)  # 设置cookie。cookie名称yl_food。cookie值 %s#%s。第一个%s为加密,后面的东西为用户uid明文。cookie保存7天

    return response


# 实现登出功能(清空cookie,跳到登录界面)
@route_user.route( "/logout" ) # 退出按钮的链接为logout
def logut():
    response  = make_response( redirect( UrlManager.buildUrl( "/user/login" )))
    response.delete_cookie( app.config['AUTH_COOKIE_NAME'] )  # 删除cookie值
    return response

