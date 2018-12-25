__author__ = '未昔'
__date__ = '2018/12/25 10:29'
# -*- coding: utf-8 -*-
"""
    编写小程序购物车逻辑
"""
from web.controllers.api import route_api
from flask import request,jsonify,g  # 前后端通过 jason来沟通
from common.models.food.Food import Food
from common.models.member.MemberCart import MemberCart
from common.libs.member.CartService import CartService  # 添加购物车，封装方法
from common.libs.Helper import selectFilterObj,getDictFilterField
from common.libs.UrlManager import UrlManager
from application import app,db
import json

@route_api.route("/cart/index")
def cartIndex():
    resp = {'code': 200, 'msg': '查询购物车成功~', 'data': {}}
    member_info = g.member_info  # 取出用户信息
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "获取失败，伪登录~~"
        return jsonify(resp)
    cart_list = MemberCart.query.filter_by(member_id=member_info.id).all()
    data_cart_list = []
    if cart_list:
        food_ids = selectFilterObj(cart_list, "food_id")  # 获取所有的 food_id
        food_map = getDictFilterField(Food, Food.id, "id", food_ids)  # 到food表里面进行查询。返回map方柏霓取值，因为它有 key
        for item in cart_list:
            tmp_food_info = food_map[item.food_id]
            tmp_data = { # 已添加的商品信息
                "id": item.id,  # 购物车商品id
                "number": item.quantity,  # 添加的数量
                "food_id": item.food_id,  # 商品id
                "name": tmp_food_info.name,   # 商品名称
                "price": str(tmp_food_info.price),
                "pic_url": UrlManager.buildImageUrl(tmp_food_info.main_image),  # 封面图
                "active": True  # 是否被选中
            }
            data_cart_list.append(tmp_data)

    resp['data']['list'] = data_cart_list
    return jsonify( resp )


@route_api.route("/cart/set", methods=["POST"])
def setCart():
    resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    req = request.values
    food_id = int(req['id']) if 'id' in req else 0  # 获得用户信息
    number = int(req['number']) if 'number' in req else 0  # 获得添加数量
    if food_id < 1 or number < 1:  # 如果商品id 或 用户id<1
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-1~~"
        return jsonify(resp)

    member_info = g.member_info  #通过api拦截器，查询当前用户。
    if not member_info: # 如果用户不存在
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-2~~"
        return jsonify(resp)

    food_info = Food.query.filter_by( id = food_id ).first()  # 判断商品是否可以收藏
    if not food_info:   # 如果没有商品信息
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-3~~"
        return jsonify(resp)

    if food_info.stock < number:  # 如果库存数量 < 添加数量
        resp['code'] = -1
        resp['msg'] = "添加购物车失败,库存不足~~"
        return jsonify(resp)

    ret = CartService.setItems( member_id=member_info.id,food_id = food_info.id,number = number )  # 添加购物车，传入要添加的值，到封装的添加购物车方法
    if not ret:  # 如果没有查到这条添加记录
        resp['code'] = -1
        resp['msg'] = "添加购物车失败-4~~"
        return jsonify(resp)
    return jsonify(resp)


@route_api.route("/cart/del", methods=["POST"])
def delCart():
    # resp = {'code': 200, 'msg': '添加购物车成功~', 'data': {}}
    # req = request.values
    # params_goods = req['goods'] if 'goods' in req else None
    #
    # items = []
    # if params_goods:
    #     items = json.loads(params_goods)
    # if not items or len(items) < 1:
    #     return jsonify(resp)
    #
    # member_info = g.member_info
    # if not member_info:
    #     resp['code'] = -1
    #     resp['msg'] = "删除购物车失败-1~~"
    #     return jsonify(resp)
    #
    # ret = CartService.deleteItem(member_id=member_info.id, items=items)
    # if not ret:
    #     resp['code'] = -1
    #     resp['msg'] = "删除购物车失败-2~~"
    #     return jsonify(resp)
    # return jsonify(resp)
    return