__author__ = '未昔'
__date__ = '2018/11/27 10:35'

from flask import render_template,g
import datetime


'''
自定义分页类
'''
def iPagination( params ):
    import math

    ret = {
        "is_prev":1,  # 是否有上一页
        "is_next":1,  # 是否有下一页
        "from" :0 ,  # from,end 模版页面循环时使用
        "end":0,
        "current":0, # 当前是多少
        "total_pages":0,  # 总页数
        "page_size" : 0,  # 每页的大小
        "total" : 0,  # 总的记录数
        "url":params['url'],  # url地址
    }

    total = int( params['total'] )
    page_size = int( params['page_size'] )
    page = int( params['page'] )
    display = int( params['display'] )  # 要展示的页数
    total_pages = int( math.ceil( total / page_size ) ) # math.ceil 用于向上取整数计算，返回的是大于或等于函数参数的数值。
    total_pages = total_pages if total_pages > 0 else 1
    if page <= 1: # 如果页数<=1，重置为0页
        ret['is_prev'] = 0

    if page >= total_pages: # 如果页数大于总页数，页重置为0页
        ret['is_next'] = 0

    semi = int( math.ceil( display / 2 ) )  # 半圆算法。假如展示10页，总页数>10时。前面展示5页，后面5页。from 前面的5页,end后面的5页

    if page - semi > 0 :
        ret['from'] = page - semi
    else:
        ret['from'] = 1

    if page + semi <= total_pages :
        ret['end'] = page + semi
    else:
        ret['end'] = total_pages

    ret['current'] = page
    ret['total_pages'] = total_pages
    ret['page_size'] = page_size
    ret['total'] = total
    ret['range'] = range( ret['from'],ret['end'] + 1 )
    return ret


"""
统一渲染方法
"""

def ops_render( template,context = {}):  # 传入模版名称，空的context上下文的变量
    if 'current_user' in g:  # 如果flask的g大变量里面有 current_user 变量
        context['current_user'] = g.current_user  # context['current_user']，就是当前用户的信息
    return  render_template( template,**context ) # 返回模版 和 当前用户信息


"""
获取当前时间
"""

def getCurrentData( format = "%Y-%m-%d %H:%M:%S"):  # 因为可能需要的时间格式不一样，所以这里设置传递一个参数。参数默认值已经设置。
    return datetime.datetime.now().strftime( format )  # formart格式化


'''
根据某个字段获取一个dic出来
'''
def getDictFilterField( db_model,select_filed,key_field,id_list ):  # 数据表。希望查询的字段。希望作为字典里面key的字段。希望的字段值
    ret = {}
    query = db_model.query
    if id_list and len( id_list ) > 0:
        query = query.filter( select_filed.in_( id_list ) )   # 用filter简单查询。这个字段的 in_ 操作

    list = query.all()  # 获得结果集。进行循环
    if not list:
        return ret
    for item in list:
        if not hasattr( item,key_field ):  # 如果没有主键，就停止不循环
            break

        ret[ getattr( item,key_field ) ] = item
    return ret

"""
    从一个对象里面取出结果
"""
def selectFilterObj( obj,field ):
    ret = []
    for item in obj:
        if not hasattr(item, field ):  # item 里面有没有这个 字段
            break
        if getattr( item,field )  in ret:
            continue
        ret.append( getattr( item,field ) ) # 添加结果，统一返回
    return ret

