# -*- coding: utf-8 -*-
from flask import Blueprint,request,redirect,jsonify
from sqlalchemy import or_

from common.libs.Helper import (ops_render,iPagination,getCurrentData)
from common.libs.member import MemberService
from common.libs.UrlManager import UrlManager
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.log.AppAccessLog import AppAccessLog
from application import app,db


route_member = Blueprint( 'member_page',__name__ )

@route_member.route( "/index" )
def index():
    """
           会员index列表页面
       """
    resp_data = {}  # 空list
    req = request.values  # 获取请求值

    page = int(req['p']) if ('p' in req and req['p']) else 1  # page是int类型。 如果page在req里面，并且有值。否则就是没有值，传1。
    query = Member.query

    # 实现搜索功能。当点击前台搜索时，链接会增加字段。
    if 'mix_kw' in req:  # 搜索界面，url参数：mix_kw（混合查询关键字）
        # 进行 all查询
        rule = or_(Member.nickname.ilike("%{0}%".format(req['mix_kw'])), Member.mobile.ilike("%{0}%".format(req['mix_kw'])))  # 定义规则。混合查询。ilike:忽略大小写
        query = query.filter(rule)

    if 'status' in req and int(req['status']) > -1:  # status查询，默认值为-1。就是有效无效的查询。
        query = query.filter(Member.status == int(req['status'])) # 查询当前状态的下的数据

    # 拿到总页数
    page_params = {
        'total': query.count(),  # 总数量
        'page_size': app.config['PAGE_SIZE'],  # 每页的大小
        'page': page,  # 当前的页数
        'display': app.config['PAGE_DISPLAY'],  # 要展示多少页，进行半圆算法
        'url': request.full_path.replace("&p={}".format(page), ""),  # 当前url路径,即page。因为 分页url里面加了个参数 &p={}，所以直接把它替换为""
    }

    pages = iPagination(page_params)  # 参数传回给 iPagination页数函数 处理
    offset = (page - 1) * app.config['PAGE_SIZE']  # 页面数据偏移量，
    limit = app.config['PAGE_SIZE'] * page  # 每页取多少数据

    # list = query.order_by(Member.id.desc()).offset( offest ).limit( app.config['PAGE_SIZE'] ).all()
    list = query.order_by(Member.id.desc()).all()[offset:limit]  # 倒序取出所有数据，会得到一个列表。[ offest:limit ] :分页计算

    resp_data['current'] = 'index'  # 数据放到这个列表里
    resp_data['list'] = list  # 数据放到这个列表里
    resp_data['pages'] = pages # 分页数据
    resp_data['search_con'] = req  # 搜索时，传递的参数
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']

    return ops_render("member/index.html", resp_data)  # 将这个json(resp_data)作为参数对象传进去



@route_member.route( "/info" )
def info():
    """
       会员详情页面
    """
    resp_data = {}  # json对象
    req = request.args  # 只取get参数
    # req = request.values # 获取参数。request.values将所有参数拼装好，放到一个字典里面
    id = int(req.get('id', 0))  # 默认值 0
    reback_url = UrlManager.buildUrl("/member/index")  # 反回列表页面

    if id < 1:  # 如果id<1，即用户不存在
        return redirect(reback_url)  # 回到列表页面

    info = Member.query.filter_by(id=id).first()  # 查询这个用户id是否存在
    if not info:  # 如果没有这个用户信息
        return redirect(reback_url)

    access_list = AppAccessLog.query.filter_by(uid=id).order_by(AppAccessLog.id.desc()).limit(10).all()
    resp_data['info'] = info  # 用户信息存在，则传给前台页面
    resp_data['access_list'] = access_list

    return ops_render("member/info.html", resp_data)


@route_member.route( "/set",methods=["GET","POST"] )
def set():
    """
     会员修改信息页面
    """
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int( req.get( "id",0 )) # 默认值传 0
        reback_url = UrlManager.buildUrl("/member/index")  # 反回列表页面

        if id<1:
            return redirect(reback_url)  # 回到列表页面

        info = Member.query.filter_by(id=id).first()  # 查询这个用户id是否存在
        if not info:  # 如果没有这个用户信息
            return redirect(reback_url)

        if info.status != 1:  # 如果 会员用户的 状态！=1，也不可以进入编辑页面
            return redirect(reback_url)

        resp_data['info'] = info
        resp_data['current'] ='index' # 光标

        return ops_render( "member/set.html",resp_data )

    # Malibu country
    resp = {'code': 200, 'msg': u"操作成功", 'data': {}}
    # 获取登录变量
    req = request.values  # 所有的请求变量，放到这个数组里

    id = req['id'] if 'id' in req else 0  # 获取在 req 里面的 会员id，没有就为0
    nickname = req['nickname'] if 'nickname' in req else ''  # 三元表达式

    if nickname is None or len(nickname) < 2 or len(nickname) >20:  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的姓名"
        return jsonify(resp)  # json 格式的转换

    member_info = Member.query.filter_by( id = id ).first()  # 判断用户 id是否存在。如果存在，那么 modle_use，就是这个用户的信息。set页面为修改用户信息
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "该会员信息不存在"
        return jsonify(resp)  # json 格式的转换

    member_info.nickname = nickname
    member_info.updated_time = getCurrentData()

    db.session.add(member_info)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功


@route_member.route( "/comment" )
def comment():
    return ops_render( "member/comment.html" )

@route_member.route("/ops",methods = [ "POST" ])
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

    member_info = Member.query.filter_by(id=id).first()  # 根据id查询用户信息是否存在。提示信息！
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "指定账号不存在"
        return jsonify(resp)  # json 格式的转换

    ## 删除、恢复，其实就是状态的改变
    if act == "remove": #如果是删除动作
        member_info.status = 0 # 将这个用户的状态status，改为0。就不显示了
    elif act == "recover":  # 如果是恢复动作
        member_info.status = 1  # 将这个用户的状态status，改为1。就显示了

    member_info.updated_time = getCurrentData() # 每次更新数据时，要记得更新时间
    db.session.add(member_info)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功


