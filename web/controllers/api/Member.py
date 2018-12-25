__author__ = '未昔'
__date__ = '2018/12/6 13:52'
## 会员入口
import requests,json   # install requests。用requests快速发送请求
from flask import request,jsonify,g # request:获取请求数据。json:和小程序进行交互式全部是通过json

from web.controllers.api import route_api  # 所有地方都是用 routr_api 进行统一注解的
from application import app,db
from common.models.member.Member import Member
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.food.WxShareHistory import WxShareHistory
from common.libs.Helper import getCurrentData
from common.libs.member.MemberService import MemberService


@route_api.route("/member/login",methods = ["GET","POST"])
def login():
    resp = { 'code':200,'msg':'操作成功','data':{} } # 定义全局变量，操作成功返回信息
    req = request.values
    code = req['code'] if 'code' in req else ''
    if not code or len(code) <1:
        resp['code'] = -1
        resp['msg'] = "需要code"
        return jsonify( resp )

    ## 通过code 可以获得用户的一些基本信息。获得的方法分到了公共方法里面
    openid = MemberService.getWeChatOpenId( code )
    if openid is None: # 如果用户的请求里面拿到的code没有 openid(用户唯一标识)
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify(resp)


    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0 # 性别
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''# 头像链接

    ## 建立数据库，确认这个openid是不是唯一的
    """
    判断是否已经注册过了，注册了直接返回一些信息
    """
    bind_info = OauthMemberBind.query.filter_by( openid=openid,type=1).first() # type=1：信息来源表示是微信用户

    if not bind_info:# 没有信息，即没注册。进行注册
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.salt = MemberService.geneSalt()  # 秘钥
        model_member.created_time = getCurrentData()
        model_member.updated_time = getCurrentData()
        db.session.add(model_member)
        db.session.commit()

        # 建立绑定关系
        model_bind = OauthMemberBind()
        model_bind.member_id = model_member.id
        model_bind.type = 1  # 信息来源1，
        model_bind.openid = openid
        model_bind.extra = ''
        model_bind.created_time = getCurrentData()
        model_bind.updated_time = getCurrentData()
        db.session.add(model_bind)
        db.session.commit()

        bind_info = model_bind  # 将新的变量赋值给 bind_info,

    member_info = Member.query.filter_by( id = bind_info.member_id).first() # 如果注册过了。会员信息 = 会员id (上面绑定用户的id)

    token = "%s#%s" % (MemberService.geneAuthCode(member_info), member_info.id)# 将token（加密字符串），返回给前台处理
    resp['data'] = {'token': token}  # 返回给前台的数据
    return jsonify( resp )


@route_api.route("/member/check-reg",methods = ["GET","POST"])
def checkReg():
    """
        验证是否已经登录过
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 定义全局变量，操作成功返回信息
    req = request.values
    code = req['code'] if 'code' in req else ''  # 判断是否存在code
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "需要code"
        return jsonify(resp)

    ## 通过code 可以获得用户的一些基本信息。获得的方法分到了公共方法里面
    openid = MemberService.getWeChatOpenId( code )
    if openid is None: # 如果用户的请求里面拿到的code没有 openid(用户唯一标识)
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        return jsonify(resp)

    ## 如果存在 openid ，验证是否已经存在绑定关系
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()  # type=1：信息来源表示是微信用户
    if bind_info is None:  # 如果OauthMemberBind（绑定关系）的表没有这个openid的信息，返回没有绑定
        resp['code'] = -1
        resp['msg'] = "未绑定"
        return jsonify(resp)

    member_info = Member.query.filter_by (id = bind_info.member_id ).first()  # 如果绑定过了。就取出会员信息
    if not member_info: # 如果是上面openid已经绑定了，但是会员表没有查到它用户id的信息
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息"
        return jsonify(resp)

    token = "%s#%s"%( MemberService.geneAuthCode( member_info ),member_info.id)
    resp['data'] = { 'token':token } # 将token（加密字符串），返回给前台处理

    return jsonify(resp)


# 小程序分享功能
@route_api.route("/member/share",methods = [ "POST" ])
def memberShare():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    url = req['url'] if 'url' in req else ''
    member_info = g.member_info  # 拦截器的方法，判断
    model_share = WxShareHistory()
    if member_info:
        model_share.member_id = member_info.id

    model_share.share_url = url
    model_share.created_time = getCurrentData()
    db.session.add(model_share)
    db.session.commit()
    return jsonify(resp)


# @route_api.route("/member/info")
# def memberInfo():
#     resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
#     member_info = g.member_info
#     resp['data']['info'] = {
#         "nickname":member_info.nickname,
#         "avatar_url":member_info.avatar
#     }
#     return jsonify(resp)