__author__ = '未昔'
__date__ = '2018/11/22 18:59'
import re
from flask import Blueprint,request,redirect,jsonify
from sqlalchemy import or_

from common.models.user import User
from common.libs.Helper import (ops_render,iPagination,getCurrentData)
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.libs.forms import REGEX_MOBILE,REGEX_Email,REGEX_LOGIN_NAME
from common.models.log.AppAccessLog import AppAccessLog
from application import app,db


route_account = Blueprint( 'account_page',__name__ )


## 账号管理页面
@route_account.route("/index")  # 加装饰方法，名字叫index
def index():
    """
        index列表页面
    """
    resp_data = {} # 空list
    req = request.values  # 获取请求值

    page = int( req['p'] ) if ('p' in req and req['p']) else 1 #page是int类型。 如果page在req里面，并且有值。否则就是没有值，传1。
    query = User.query

    # 实现搜索功能。当点击前台搜索时，链接会增加字段。
    if 'mix_kw' in req:  # 搜索界面，url参数：mix_kw（混合查询关键字）
       # 进行 all查询
        rule = or_( User.nickname.ilike( "%{0}%".format( req['mix_kw']) ),User.email.ilike( "%{0}%".format( req['mix_kw']) ),User.mobile.ilike( "%{0}%".format( req['mix_kw']) ) ) # 定义规则。混合查询。ilike:忽略大小写
        query = query.filter( rule )

    if 'status' in req and int( req['status']) >-1:  # status查询，默认值为-1。就是有效无效的查询。
        query = query.filter( User.status == int( req['status']) )


    # 拿到总页数
    page_params = {
        'total':query.count(),  # 总页数
        'page_size':app.config['PAGE_SIZE'],  # 每页的大小
        'page': page,  # 当前的页数
        'display':app.config['PAGE_DISPLAY'],  # 要展示多少页，进行半圆算法
        'url':request.full_path.replace( "&p={}".format(page),""), # 当前url路径,即page。因为 分页url里面加了个参数 &p={}，所以直接把它替换为""

        # 'url': '/account/index',  # 当前url路径
    }

    pages = iPagination( page_params )  # 参数传回给 iPagination页数函数 处理
    offset = (page-1) * app.config['PAGE_SIZE'] #   页面数据偏移量，
    limit = app.config['PAGE_SIZE'] * page #  每页取多少数据

    list = query.order_by( User.uid.desc() ).all()[ offset:limit ] # 倒序取出所有数据，会得到一个列表。[ offest:limit ] :分页计算

    resp_data['list'] = list  # 数据放到这个列表里
    resp_data['pages'] = pages
    resp_data['search_con'] = req  # 搜索时，传递的参数
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render( "account/index.html",resp_data )  # 将这个json(resp_data)作为参数对象传进去


@route_account.route("/info")
def info(): 
    """
    详情页面
    """
    resp_data = {} # json对象
    req = request.args  # 只取get参数
    # req = request.values # 获取参数。request.values将所有参数拼装好，放到一个字典里面
    uid = int( req.get('id',0))  # 默认值 0
    reback_url = UrlManager.buildUrl("/account/index")# 反回列表页面
    if uid<1:  # 如果id<1，即用户不存在
        return redirect( reback_url )  # 回到列表页面

    info = User.query.filter_by( uid=uid ).first() # 查询这个用户id是否存在
    if not info: # 如果没有这个用户信息
        return redirect( reback_url )

    access_list = AppAccessLog.query.filter_by(uid=uid).order_by(AppAccessLog.id.desc()).limit(10).all()
    resp_data['info'] = info  # 用户信息存在，则传给前台页面
    resp_data['access_list'] = access_list

    return ops_render("account/info.html",resp_data)


@route_account.route("/set",methods = ["GET","POST"])  # 两种请求方式，因为涉及表单提交.(编写ajax提交数据)
def set():
    """
        修改个人信息页面、添加账号信息页面
    """
    default_pwd = "******"
    if request.method == "GET":
        resp_data = {}
        req = request.args
        uid = int( req.get("id",0) )
        info = None  # 因为如果是添加信息，那么上个页面，就不会传回id，所以为None，进入添加账号页面。否则点击编辑就传回id，进入修改信息页面
        if uid:
            info = User.query.filter_by( uid=uid ).first() # filter_by不用写类，他会自动区分的
        resp_data['info'] = info # 统一渲染的 resp_data(json)里面，将user_info放进去
        return ops_render( "account/set.html",resp_data )

    resp = {'code': 200, 'msg': u"操作成功", 'data': {}}
    # 获取登录变量
    req = request.values  # 所有的请求变量，放到这个数组里

    id = req['id'] if 'id' in req else 0  # id 是用来判断是增加用户信息，还是修改用户信息
    nickname = req['nickname'] if 'nickname' in req else ''  # 三元表达式
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    if nickname is None or len(nickname) < 2 or len(nickname) >15:  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify(resp)  # json 格式的转换

    if mobile is None or not re.match(REGEX_MOBILE,mobile):  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的手机号码"
        return jsonify(resp)  # json 格式的转换

    if email is None or not re.match(REGEX_Email,email):  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的邮箱"
        return jsonify(resp)  # json 格式的转换

    if login_name is None or not re.match(REGEX_LOGIN_NAME,login_name):  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录名"
        return jsonify(resp)  # json 格式的转换

    if login_pwd is None or len(login_pwd) < 6 or len(login_pwd) > 15:  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的登录密码"
        return jsonify(resp)  # json 格式的转换

    has_in = User.query.filter( User.login_name == login_name,User.uid != id).first()
    # login_name判断用户是否存在。User.uid != id：这个表明是该用户id不存在，即为增加用户信息。filter支持的方式更多一点。filter_by只能传一个json

    if has_in:  # 如果用户名已经存在了
        resp['code'] = -1
        resp['msg'] = "该登录名已存在，请重新输入"
        return jsonify(resp)  # json 格式的转换

    user_info = User.query.filter_by( uid=id ).first()  # 判断用户 id是否存在。如果存在，那么 modle_use，就是这个用户的信息。set页面为修改用户信息
    if user_info:
        modle_use = user_info
    else:  # 否则，就是这个uid不存在。那么久为增加用户信息界面
        modle_use = User()
        modle_use.created_time = getCurrentData() # 增加用户信息时，created_time才改变
        modle_use.login_salt = UserService.geneSalt() # geneSalt即数据库salt字段， 自定义的加密规则。增加用户信息，才会生成salt

    modle_use.nickname = nickname
    modle_use.mobile = mobile
    modle_use.email = email
    modle_use.login_name = login_name
    if login_pwd != default_pwd:  # 如果传回来的密码value，不是default密码，那么就改密码，反之不改密码。
        modle_use.login_pwd = UserService.genePwd( login_pwd,modle_use.login_salt ) # 加密后的密码，就是前面定义的，通过密码和 salt进行加密
        resp['msg'] = "操作成功，登录用户 %s 的密码为：%s"%(login_name,login_pwd)
    modle_use.updated_time = getCurrentData()

    db.session.add(modle_use)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功


@route_account.route("/ops",methods = [ "POST" ])
def ops():
    """
        删除、恢复账号
    """
    ## 都是用json，ajax提交，所以定义头部
    resp = {'code': 200, 'msg': u"操作成功", 'data': {}}
    req = request.values

    # 操作过程
    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not id:  # 如果没有id
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号"
        return jsonify(resp)  # json 格式的转换

    if act not in ['remove','recover']:  # 这样写，防止伪造js
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试"
        return jsonify(resp)  # json 格式的转换

    user_info = User.query.filter_by(uid=id).first()  # 根据id查询用户信息是否存在。提示信息！
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "指定账号不存在"
        return jsonify(resp)  # json 格式的转换

    ## 删除、恢复，其实就是状态的改变
    if act == "remove": #如果是删除动作
        user_info.status = 0 # 将这个用户的状态status，改为0。就不显示了
    elif act == "recover":  # 如果是恢复动作
        user_info.status = 1  # 将这个用户的状态status，改为1。就显示了

    user_info.updated_time = getCurrentData() # 每次更新数据时，要记得更新时间
    db.session.add(user_info)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功





