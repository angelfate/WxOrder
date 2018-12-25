__author__ = '未昔'
__date__ = '2018/11/21 18:56'
# 基础配置（公用）
DEBUG = False
SERVER_PORT = 8999  # 运行端口
SQLALCHEMY_ECHO = False   # base 里面默认都是false

AUTH_COOKIE_NAME = "yl_food"

## 过滤url，静态页面和 登录页面不需要重新登录（拦截器里面）
IGNORE_URLS = [
    "^/user/login",
]

IGNORE_CHECK_LOGIN_URLS = [  # 完全不需要判断的
    "^/static",  # 如果是 static， 完全不需要判断登录，因为静态文件查询也没意思
    "^/favicon.ico"
]

## 过滤小程序不需要拦截的url。静态页面和 登录页面不需要重新登录（拦截器里面）
API_IGNORE_URLS = [
    "^/api",
]

PAGE_SIZE = 20 # 分页每页的大小
PAGE_DISPLAY = 10 # 展示多少页

STATUS_MAPPING = { # 状态
    "1":"正常",
    "0":"已删除",
}

MINA_APP = { # 小程序秘钥
    'appid':'wxb4f07dc6c2517312',
    'appkey':'5f22c7439f1dfe59780f71ef6ad22a08',
}

UPLOAD = {
    'ext':['jpg','gif','bmp','jpeg','png'],  # 支持上传的图片格式
    'prefix_path': '/web/static/upload/', #前缀路径。上传图片的目录
    'prefix_url': '/static/upload/'  # url地址.(PS：因为static.py配置文件设置过。所以默认的配置文件直接从static里面读的，就不要写web了)
}

APP = { # 图片上传，之后的绝对地址
    'domain':'http://127.0.0.1:8999' #域名

}

