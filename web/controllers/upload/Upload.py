__author__ = '未昔'
__date__ = '2018/12/19 15:11'
# -*- coding: utf-8 -*-
from flask import Blueprint,request,jsonify
from application import app,db
import re,json
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager  # 上传后的图片地址方法
from common.models.Image import Image

route_upload = Blueprint('upload_page', __name__)

'''
参考文章：https://segmentfault.com/a/1190000002429055
'''

@route_upload.route("/ueditor",methods = [ "GET","POST" ])
def ueditor():

    req = request.values
    action = req['action'] if 'action' in req else ''  # 动作

    if action == "config":
        root_path = app.root_path
        config_path = "{0}/web/static/plugins/ueditor/upload_config.json".format( root_path )
        with open( config_path,encoding="utf-8" ) as fp:
                try:
                    config_data = json.loads( re.sub( r'\/\*.*\*/' ,'',fp.read() ) )
                except:
                    config_data = {}
        return jsonify( config_data )

    if action == "uploadimage":  # 上传图片动作
        return uploadImage()

    if action == "listimage":  #图片在线管理
        return listImage()  # 返回所有上传的的图片

    return "upload"


@route_upload.route("/pic",methods = [ "GET","POST" ])
def uploadPic():
    file_target = request.files
    upfile = file_target['pic'] if 'pic' in file_target else None
    callback_target = 'window.parent.upload'  # 调用父页面
    if upfile is None:  # 返回的js是的error事件，将事件放到{1}里面。
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format( callback_target,"上传失败" )

    ret = UploadService.uploadByFile(upfile)  #上传图片
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target, "上传失败：" + ret['msg'])

    return "<script type='text/javascript'>{0}.success('{1}')</script>".format(callback_target,ret['data']['file_key'] )  #返回的是file_key


# 上传图片方法
def uploadImage():
    resp = { 'state':'SUCCESS','url':'','title':'','original':'' }
    file_target = request.files  # 获取请求文件参数
    app.logger.info( file_target )
    # ImmutableMultiDict([('upfile', < FileStorage: 'about_img.png' ('image/png') >)])  # <-- key,文件名，类型 -->
    upfile = file_target['upfile'] if 'upfile' in file_target else None # Key值：upfile
    if upfile is None:
        resp['state'] = "上传失败"
        return jsonify(resp)

    # 如果成功了，就说明有图片，那么进入统一封装好的上传方法
    # 封装的前提是，上传的动作是通用的和业务一点关系也没有，所以进行统一封装。做成api
    ret = UploadService.uploadByFile( upfile ) #
    if ret['code'] != 200:
        resp['state'] = "上传失败：" + ret['msg']
        return jsonify(resp)

    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])  # 上传后的图片url
    return jsonify(resp)


# 实现图片在线管理
def listImage():
    resp = {'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0} # 请求拿到的动作数据。action: listimage，所以放的是list

    req = request.values

    start = int(req['start']) if 'start' in req else 0  # 初始值
    page_size = int(req['size']) if 'size' in req else 20  #每页大小

    query = Image.query
    if start > 0:
        query = query.filter(Image.id < start)  # 倒序拍的，所以id越来越小

    list = query.order_by(Image.id.desc()).limit(page_size).all() #id倒序查出所有图片。offest:页面偏移量。limit：图片的数量
    images = []  # 返回的是一个数组

    if list: #如果list存在
        for item in list: # 进行循环
            images.append({'url': UrlManager.buildImageUrl(item.file_key)})  # 字典，添加url地址
            start = item.id
    resp['list'] = images
    resp['start'] = start
    resp['total'] = len(images)
    return jsonify( resp )

