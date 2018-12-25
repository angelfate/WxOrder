__author__ = '未昔'
__date__ = '2018/12/23 13:20'
# -*- coding: utf-8 -*-

## 会员入口
import requests,json   # install requests。用requests快速发送请求
from flask import request,jsonify,g # request:获取请求数据。json:和小程序进行交互式全部是通过json

from web.controllers.api import route_api  # 所有地方都是用 routr_api 进行统一注解的
from application import app,db
from common.libs.Helper import getCurrentData
from common.libs.UrlManager import UrlManager
from common.libs.Helper import getCurrentData,getDictFilterField
from common.models.food.FoodCat import FoodCat  # 菜品分类
from common.models.food.Food import Food  # 搜索、展示。并且以比较火的图片做成banner图
from common.models.member.MemberCart import MemberCart
from application import app,db
from sqlalchemy import  or_


#返回banner图，及首页的分类信息
@route_api.route("/food/index")
def foodIndex():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 定义全局变量，操作成功返回信息
    cat_list = FoodCat.query.filter_by( status=1 ).order_by( FoodCat.weight.desc() ).all()  # 状态为1的菜品，按照权重倒序排序
    data_cat_list = [] # 返回数据构造。因为全部里面不会一次展示所有数据
    data_cat_list.append({  # 先将全部数据放进来
        'id':0,
        'name':'全部',
    })
    if cat_list:  # 如果数据库可以查到cat_list 字段
        for item in cat_list:  # 循环展示
            tmp_data = {   # 构造一个字典类型
                "id":item.id,
                "name":item.name,
            }
            data_cat_list.append( tmp_data )  # 将所有数据添加到数组里面。就可以获得类别的数据
    resp['data']['cat_list'] = data_cat_list

    food_list = Food.query.filter_by( status=1 ).\
        order_by( Food.total_count.desc(),Food.id.desc()).limit(3).all()  # 按照销售额和id倒序排，将销售量最大的展示出来

    data_food_list = []  # 格式化，返回给前端
    if food_list:
        for item in food_list:  # banner展示的数据
            tmp_data = {
                "id": item.id,
                "pic_url": UrlManager.buildImageUrl(item.main_image),
            }
            data_food_list.append(tmp_data)  # 将所有数据添加到数组里面。就可以获得类别的数据
    resp['data']['banner_list'] = data_food_list

    return jsonify( resp )  # 返回 json数据


#返回搜索信息
@route_api.route("/food/search")
def foodSearch():
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    req = request.values  # 获得请求的数据
    cat_id = int( req['cat_id'] ) if 'cat_id' in req else 0   # 表单里面的 分类id
    mix_kw = str( req['mix_kw'] ) if 'mix_kw' in req else ''
    p = int(req['p']) if 'p' in req else 1   #获取请求里面的 分页 p 值

    if p < 1:
        p = 1

    page_size = 10
    offset = (p - 1) * page_size
    query = Food.query.filter_by(status=1)

    if cat_id > 0:
        query = query.filter_by(cat_id=cat_id)

    if mix_kw:
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)), Food.tags.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    food_list = query.order_by(Food.total_count.desc(), Food.id.desc()) \
        .offset(offset).limit(page_size).all()

    data_food_list = []
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': "%s" % (item.name),
                'price': str(item.price),
                'min_price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            data_food_list.append(tmp_data)
    resp['data']['list'] = data_food_list
    resp['data']['has_more'] = 0 if len(data_food_list) < page_size else 1  # 判断是否还有数据。如果取出来的数据数量小于 每页数量，就说明没了
    return jsonify(resp)


# 商品详情
@route_api.route("/food/info" )
def foodInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req else 0
    food_info = Food.query.filter_by( id = id ).first()
    if not food_info or not food_info.status :  # 没有信息 或者 状态 ！=1
        resp['code'] = -1
        resp['msg'] = "美食已下架"
        return jsonify(resp)

    member_info = g.member_info  # 获取当前用户，来显示购物车数量
    cart_number = 0  # 初始数量为0
    if member_info:
        cart_number = MemberCart.query.filter_by( member_id =  member_info.id ).count()
    resp['data']['info'] = {
        "id":food_info.id,
        "name":food_info.name,
        "summary":food_info.summary,  #描述
        "total_count":food_info.total_count,  #总销售数
        "comment_count":food_info.comment_count,  # 总评论数
        'main_image':UrlManager.buildImageUrl( food_info.main_image ),
        "price":str( food_info.price ),  # json需要把 int换成字符串
        "stock":food_info.stock,
        "pics":[ UrlManager.buildImageUrl( food_info.main_image ) ]  # 图片
    }
    resp['data']['cart_number'] = cart_number
    return jsonify(resp)

# @route_api.route("/food/comments")
# def foodComments():
#     resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
#     req = request.values
#     id = int(req['id']) if 'id' in req else 0
#     query = MemberComments.query.filter( MemberComments.food_ids.ilike("%_{0}_%".format(id)) )
#     list = query.order_by( MemberComments.id.desc() ).limit(5).all()
#     data_list = []
#     if list:
#         member_map = getDictFilterField( Member,Member.id,"id",selectFilterObj( list,"member_id" ) )
#         for item in list:
#             if item.member_id not in member_map:
#                 continue
#             tmp_member_info = member_map[ item.member_id ]
#             tmp_data = {
#                 'score':item.score_desc,
#                 'date': item.created_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "content":item.content,
#                 "user":{
#                     'nickname':tmp_member_info.nickname,
#                     'avatar_url':tmp_member_info.avatar,
#                 }
#             }
#             data_list.append( tmp_data )
#     resp['data']['list'] = data_list
#     resp['data']['count'] = query.count()
#     return jsonify(resp)