# -*- coding: utf-8 -*-
from flask import Blueprint,request,redirect,jsonify
from sqlalchemy import or_  # 搜索框，用到的混合查询
from decimal import Decimal

from application import app,db
from common.libs.Helper import ops_render,getCurrentData,iPagination,getDictFilterField
from common.libs.UrlManager import UrlManager
from common.libs.food.FoodService import FoodService
from common.models.food.Food import Food
from common.models.food.FoodCat import FoodCat
from common.models.food.FoodStockChangeLog import FoodStockChangeLog


route_food = Blueprint( 'food_page',__name__ )

@route_food.route( "/index" )
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取p 参数
    query = Food.query
    if 'mix_kw' in req:  # or_ 来模糊查询
        rule = or_(Food.name.ilike("%{0}%".format(req['mix_kw'])), Food.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)  # 加入规则

    if 'status' in req and int(req['status']) > -1:  # 菜品状态查询
        query = query.filter(Food.status == int(req['status']))

    if 'cat_id' in req and int(req['cat_id']) > 0:  # 菜品分类 查询
        query = query.filter(Food.cat_id == int(req['cat_id']))

    page_params = {  # 分页参数
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)  # 回传分页参数
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量
    list = query.order_by(Food.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()  # limit限制返回的数据大小

    cat_mapping = getDictFilterField(FoodCat, FoodCat.id, "id", [])   # [] 说明要查 id=所有，的字段
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['cat_mapping'] = cat_mapping
    resp_data['current'] = 'index'
    return ops_render("food/index.html", resp_data)

@route_food.route( "/info" )
def info():
    resp_data = {}
    req = request.args
    id = int(req.get("id", 0))
    reback_url = UrlManager.buildUrl("/food/index")

    if id < 1:
        return redirect(reback_url)

    info = Food.query.filter_by(id=id).first()
    if not info:
        return redirect(reback_url)

    stock_change_list = FoodStockChangeLog.query.filter(FoodStockChangeLog.food_id == id) \
        .order_by(FoodStockChangeLog.id.desc()).all()  # 这个是查询库存变更记录

    resp_data['info'] = info
    resp_data['stock_change_list'] = stock_change_list
    resp_data['current'] = 'index'
    return ops_render("food/info.html", resp_data)


@route_food.route( "/set", methods=['GET', 'POST'])
def set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int( req.get('id', 0))  # 获取查询的美食信息 id
        info = Food.query.filter_by(id=id).first()  # 获取美食信息
        if info and info.status != 1: # 如果存在info，但是它的状态 !=1，即被删除了，那么返回首页
            return redirect(UrlManager.buildUrl("/food/index"))

        cat_list = FoodCat.query.all()  # 查询所有分类
        resp_data['info'] = info
        resp_data['cat_list'] = cat_list
        resp_data['current'] = 'index'
        return ops_render("food/set.html", resp_data)

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values
    id = int(req['id']) if 'id' in req and req['id'] else 0
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    name = req['name'] if 'name' in req else ''
    price = req['price'] if 'price' in req else ''
    main_image = req['main_image'] if 'main_image' in req else ''  #封面图
    summary = req['summary'] if 'summary' in req else ''
    stock = int(req['stock']) if 'stock' in req else ''  # 库存
    tags = req['tags'] if 'tags' in req else ''   # 标签

    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择分类~~"
        return jsonify(resp)

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称~~"
        return jsonify(resp)

    if not price or len(price) <=0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    price = Decimal(price).quantize(Decimal('0.00'))  # 价格，换成0.00
    if price <= 0:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的售卖价格~~"
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = "请上传封面图~~"
        return jsonify(resp)

    if summary is None or len(summary) < 3:
        resp['code'] = -1
        resp['msg'] = "请输入图书描述，并不能少于10个字符~~"
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的库存量~~"
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入标签，便于搜索~~"
        return jsonify(resp)

    food_info = Food.query.filter_by(id=id).first()
    before_stock = 0  # 改变之前的 库存
    if food_info:
        model_food = food_info
        before_stock = model_food.stock # 修改时，当前库存量before_stock就是 数据表里面的
    else:
        model_food = Food()
        model_food.status = 1
        model_food.created_time = getCurrentData()

    model_food.cat_id = cat_id  # 库存变更表记录
    model_food.name = name
    model_food.price = price
    model_food.main_image = main_image
    model_food.summary = summary
    model_food.stock = stock
    model_food.tags = tags
    model_food.updated_time = getCurrentData()

    db.session.add(model_food)
    ret = db.session.commit()

    FoodService.setStockChangeLog(model_food.id, int(stock) - int(before_stock), "后台修改")  # 商品数量变更记录。商品id，变更的数量，备注
    return jsonify(resp)



@route_food.route( "/cat" )
def cat():
    """
           菜品分类展示页面
    """
    resp_data = {}  # 空list
    req = request.values  # 获取请求值

    page = int(req['p']) if ('p' in req and req['p']) else 1  # page是int类型。 如果page在req里面，并且有值。否则就是没有值，传1。
    query = FoodCat.query

    # 实现搜索功能。当点击前台搜索时，链接会增加字段。
    if 'mix_kw' in req:  # 搜索界面，url参数：mix_kw（混合查询关键字）
        # 进行 all查询
        rule = or_(FoodCat.name.ilike("%{0}%".format(req['mix_kw'])))  # 定义规则。混合查询。ilike:忽略大小写
        query = query.filter(rule)

    if 'status' in req and int(req['status']) > -1:  # status查询，默认值为-1。就是有效无效的查询。
        query = query.filter(FoodCat.status == int(req['status']))  # 查询当前状态的下的数据


    # 拿到总页数
    page_params = {
        'total': query.count(),  # 总页数
        'page_size': app.config['PAGE_SIZE'],  # 每页的大小
        'page': page,  # 当前的页数
        'display': app.config['PAGE_DISPLAY'],  # 要展示多少页，进行半圆算法
        'url': request.full_path.replace("&p={}".format(page), ""),  # 当前url路径,即page。因为 分页url里面加了个参数 &p={}，所以直接把它替换为""
    }

    pages = iPagination(page_params)  # 参数传回给 iPagination页数函数 处理
    offset = (page - 1) * app.config['PAGE_SIZE']  # 页面数据偏移量，
    limit = app.config['PAGE_SIZE'] * page  # 每页取多少数据

    list = query.order_by(FoodCat.weight.desc(),FoodCat.id.desc()).all()[offset:limit]  # 倒序按weight和id排序 取出所有数据，会得到一个列表。[ offest:limit ] :分页计算

    resp_data['list'] = list  # 数据放到这个列表里
    resp_data['pages'] = pages
    resp_data['current'] = 'cat'
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['search_con'] = req  # 搜索时，传递的参数

    return ops_render( "food/cat.html",resp_data )

@route_food.route( "/cat-set",methods=["GET","POST"] ) # get页面数据展示，post数据提交
def catSet():
    """
        菜品分类的 编辑和添加（编辑会查到菜的id修改信息，添加不到id）
    """
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int(req.get("id", 0))
        info = None  # 因为如果是添加信息，那么上个页面，就不会传回id，所以为None，进入添加账号页面。否则点击编辑就传回id，进入修改信息页面
        if id:
            info = FoodCat.query.filter_by( id=id ).first()  # filter_by不用写类，他会自动区分的

        resp_data['info'] = info  # 统一渲染的 resp_data(json)里面，将user_info放进去
        resp_data['current'] = 'cat'
        return ops_render("food/cat_set.html", resp_data)

    resp = {'code': 200, 'msg': u"操作成功", 'data': {}}
    # 获取登录变量
    req = request.values  # 所有的请求变量，放到这个数组里

    id = req['id'] if 'id' in req else 0  # id 是用来判断是增加用户信息，还是修改用户信息
    name = req['name'] if 'name' in req else ''  # 三元表达式
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else ''

    if name is None or len(name) < 2 or len(name) > 12:  # 进行参数判断
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的分类名称"
        return jsonify(resp)  # json 格式的转换

    food_cat_info = FoodCat.query.filter_by(id=id).first()  # 判断食品 id是否存在。如果存在，那么 modle_use，就是这个食品的信息。set页面为修改用户信息
    if food_cat_info:
        modle_cat_info = food_cat_info
    else:  # 否则，就是这个uid不存在。那么久为增加用户信息界面
        modle_cat_info = FoodCat()
        modle_cat_info.created_time = getCurrentData()  # 增加用户信息时，created_time才改变

    modle_cat_info.name = name
    modle_cat_info.weight = weight
    modle_cat_info.updated_time = getCurrentData()

    db.session.add(modle_cat_info)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功



@route_food.route("/cat-ops",methods = [ "POST" ])
def CatOps():
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
        resp['msg'] = "请选择要操作的菜品分类"
        return jsonify(resp)  # json 格式的转换

    if act not in ['remove','recover']:  # 这样写，防止伪造js（如果act状态里面）
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试"
        return jsonify(resp)  # json 格式的转换

    food_cat_info = FoodCat.query.filter_by(id=id).first()  # 根据id查询菜品分类信息是否存在。提示信息！
    if not food_cat_info:
        resp['code'] = -1
        resp['msg'] = "指定菜品分类不存在"
        return jsonify(resp)  # json 格式的转换

    ## 删除、恢复，其实就是状态的改变
    if act == "remove": #如果是删除动作
        food_cat_info.status = 0 # 将这个用户的状态status，改为0。就不显示了
    elif act == "recover":  # 如果是恢复动作
        food_cat_info.status = 1  # 将这个用户的状态status，改为1。就显示了

    food_cat_info.updated_time = getCurrentData() # 每次更新数据时，要记得更新时间
    db.session.add(food_cat_info)  # 数据库添加数据，统一提交
    db.session.commit()
    return jsonify(resp)  # 返回信息，更改成功


@route_food.route("/ops",methods=["POST"])
def ops():
    resp = { 'code':200,'msg':'操作成功~~','data':{} }
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''

    if not id :
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify(resp)

    if act not in [ 'remove','recover' ]:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"
        return jsonify(resp)

    food_info = Food.query.filter_by( id = id ).first()
    if not food_info:
        resp['code'] = -1
        resp['msg'] = "指定美食不存在~~"
        return jsonify(resp)

    if act == "remove":
        food_info.status = 0
    elif act == "recover":
        food_info.status = 1

    food_info.updated_time = getCurrentData()
    db.session.add(food_info)
    db.session.commit()
    return jsonify( resp )
