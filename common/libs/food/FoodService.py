# -*- coding: utf-8 -*-
from application import app, db
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.models.food.Food import Food
from common.libs.Helper import getCurrentData


class FoodService():

    @staticmethod# 库存变更记录
    def setStockChangeLog(food_id=0, quantity=0, note=''):  # 商品id，变更的数量，备注信息

        if food_id < 1:
            return False

        food_info = Food.query.filter_by(id=food_id).first()
        if not food_info:
            return False

        model_stock_change = FoodStockChangeLog()
        model_stock_change.food_id = food_id
        model_stock_change.unit = quantity
        model_stock_change.total_stock = food_info.stock
        model_stock_change.note = note
        model_stock_change.created_time = getCurrentData()
        db.session.add(model_stock_change)
        db.session.commit()
        return True
