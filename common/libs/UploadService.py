__author__ = '未昔'
__date__ = '2018/12/20 19:19'
from werkzeug.utils import secure_filename # 用这个来获得安全文件名
import os,stat,uuid # os判断路径。stat给文件加权限.uuid查询命名文件名（工具硬件和时间生成唯一的不重复的字符串）

from common.libs.Helper import getCurrentData
from common.models.Image import Image
from application import app,db

"""
上传图片方法（全静态方法）
"""

class UploadService():
    @staticmethod
    def uploadByFile(file): # 定义上传文件函数。参数是文件类
        config_upload = app.config['UPLOAD']
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}
        filename = secure_filename(file.filename) # 获得上传的文件名
        ext = filename.rsplit(".", 1)[1]  # 获得类型（扩展名）。即文件名以.切割，拿到后面部分。
        if ext not in config_upload['ext']:
            resp['code'] = -1
            resp['msg'] = "不允许的扩展类型文件"
            return resp

        root_path = app.root_path + config_upload['prefix_path']  # 图片存放路径。app.root_path获取全局路径
        file_dir = getCurrentData("%Y%m%d")  # 按照日期生成文件夹
        save_dir = root_path + file_dir  # 最终的保存地址
        if not os.path.exists( save_dir ):
            os.mkdir(save_dir)
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO )  # 给这个文件赋予权限。拥有者最高权限|。权限参考：http://www.runoob.com/python/os-chmod.html

        file_name = str(uuid.uuid4()).replace("-", "") + "." + ext  # 重命名文件名
        file.save("{0}/{1}".format(save_dir, file_name))  # 保存文件。在save_dir路径下

        # 存储图片路径到数据库
        model_image = Image()
        model_image.file_key = file_dir + "/" + file_name
        model_image.created_time = getCurrentData()
        db.session.add(model_image)
        db.session.commit()

        resp['data'] = {
            'file_key': file_dir + "/" + file_name
        }
        return resp
