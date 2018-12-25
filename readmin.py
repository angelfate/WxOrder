__author__ = '未昔'
__date__ = '2018/11/21 19:47'
"""
   =====================order说明=====================

common：存放共用部分
    libs：公共方法或者类
    models：所有的数据库model

config：配置文件
    base_setting：基础配置
    develop_setting ：开发环境
    local_setting_demo：本地开发环境demo
    production_setting：生产环境的配置

docs：文档存放
    mysql.md：所有数据库变更必须在这里记录

jobs：定时任务
    tasks：所有定时任务都存放在这里

manage.py：启动入口

release.sh：系统自己的简单操作脚本

requirements.txt：Python 扩展

uwsgi.ini ：生产环境

web：HTTP存放
    controllers：所有的C层放在这里
    interceptors：拦截器相关
    static：静态文件
    templates：模版文件
        common:统一布局（存放共同的h5页面，即base模版）

www.py  ：HTTP模版相关初始化

application：封装app和方法

"""



"""
    ===============mina 小程序说明=====================

app.json：放的是所有页面。
app.js：简单定义

page：放的是所有页面模版

images：所有的图片
PS：很多图片要放到cdn或者base64。因为 小程序的 wxss文件，很多时候不让从本地里面读取背景文件路径

"""



"""
    =====================操作=====================
映射数据库model文件：
    flask-sqlacodegen "mysql://root:@127.0.0.1/food_db" --tables user --outfile "common/models/user.py" --flask

flask打印信息：
    app.logger.info( auth_cookie ) 
    app.logger.debug( auth_cookie )
    
清空表数据：truncate table 表名称 ;
    select * from app_access_log;
    truncate table app_access_log;
    truncate table app_error_log;
    
显示表结构：show create table table_name \G;
"""

"""
发布时要更改的地方：
    (127的本地url好像不用换吧)
    1、base_setting,要换成production_setting.py。通过环境变量来，怎么改变参考前面。（把applica.py里面其他配置文件删了）
    2、web/static/js/common.js下面的buildPicUrl里面有，绝对地址。替换掉
    3、mina/app.js 的domain好像需要换掉
    
"""

"""
每天要用到的命令
    cmder：
        cd E:\Envs\Small_program\order
        e:
        workon Small_program
        python manage.py runserver
    
    cmd:
        mysql -uroot -p
        show databases;
        use food_db;
        show tables;
        select * from 
        show create table  \G; 
        
    https://developers.weixin.qq.com/miniprogram/dev/api/api-login.html（旧版 · 已经不更新）
    https://developers.weixin.qq.com/miniprogram/dev/api/wx.login.html（新版本）
    https://developers.weixin.qq.com/miniprogram/dev/framework/MINA.html（新版本）        
"""