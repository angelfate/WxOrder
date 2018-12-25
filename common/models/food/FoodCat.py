# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db,app

class FoodCat(db.Model): # 食品分类表
    __tablename__ = 'food_cat'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    weight = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @property  # 装饰器，虚拟属性
    def status_desc(self): # 状态描述
        return app.config['STATUS_MAPPING'][ str(self.status) ] #  self.status：当前的数据的status。字典里面用的是字符串


