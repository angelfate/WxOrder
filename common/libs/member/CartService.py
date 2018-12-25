# -*- coding: utf-8 -*-
"""
    封装购物车业务逻辑
"""
import hashlib,requests,random,string,json
from application import app,db
from common.models.member.MemberCart import MemberCart
from common.libs.Helper import getCurrentData


class CartService():

    @staticmethod
    def deleteItem( member_id = 0,items = None ):  # 删除购物车数据
        if member_id < 1 or not items:
            return False
        for item in items:
            MemberCart.query.filter_by( food_id = item['id'],member_id = member_id ).delete()
        db.session.commit()
        return True

    # 添加和变更购物车数据
    @staticmethod
    def setItems( member_id = 0,food_id = 0,number = 0 ):  # 用户id，商品id，添加数量
        if member_id < 1 or food_id < 1 or number < 1:  # 如果任何一个值小于1
            return False

        # 添加和更新，判断这个信息是否存在（用户和商品 id 是否相同）
        cart_info = MemberCart.query.filter_by( food_id = food_id, member_id= member_id ).first()
        if cart_info:  # 如果购物车数据表，有这个添加信息。就是set更新
            model_cart = cart_info
        else:  # 没有就是，添加新的信息
            model_cart = MemberCart()
            model_cart.member_id = member_id
            model_cart.created_time = getCurrentData()

        model_cart.food_id = food_id
        model_cart.quantity = number
        model_cart.updated_time = getCurrentData()
        db.session.add(model_cart)
        db.session.commit()
        return True

