# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class UserIp(db.Model):
    __tablename__ = 'user_ip'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime)
