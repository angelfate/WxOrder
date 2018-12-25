__author__ = '未昔'
__date__ = '2018/12/8 22:27'

import hashlib,base64,random,string,json,requests

from application import app


class MemberService():  # 用来编写user表的核心操作

    @staticmethod
    def geneAuthCode( member_info=None ):  # 产生授权码
        m = hashlib.md5()  # 实例化
        str = "%s-%s-%s"%( member_info.id,member_info.salt,member_info.status) # id是唯一的。salt是秘钥。status是状态。如果被删除了，也不能登陆
        m.update(str.encode("utf-8"))
        return m.hexdigest()  # 每次取出用户的uid，然后通过这个加密字符串，判断用户的 cookie 是否改变。


    @staticmethod  # 静态方法
    def geneSalt( length=16 ): # 定义 数据库salt字段，即密码加密规则
        #  string所有的ascii + string的数字，组成一个字符串。通过 for i in range(length) 取出16位。
        keylist = [random.choice( (string.ascii_letters + string.digits) ) for i in range(length)]
        return ("".join(keylist))  # 进行拼接


    @staticmethod  # 静态方法
    def getWeChatOpenId( code ):  # 获得微信用户的openid
        ## 通过code 可以获得用户的一些基本信息
        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(app.config['MINA_APP']['appid'], app.config['MINA_APP']['appkey'], code)  # 将base的小程序id和秘钥放进来

        r = requests.get(url)
        res = json.loads(r.text)
        openid = None
        if 'openid' in res: # 如果 请求里面有 openid
            openid = res['openid']  # 将 openid字符串 解析成json。openid在json字符串里面统一获取
        return openid



