__author__ = '未昔'
__date__ = '2018/11/25 17:03'
import hashlib,base64,random,string


class UserService():  # 用来编写user表的核心操作

    @staticmethod
    def geneAuthCode( user_info=None ):  # 产生授权码
        m = hashlib.md5()  # 实例化
        str = "%s-%s-%s-%s"%( user_info.uid,user_info.login_name,user_info.login_pwd,user_info.login_salt)
        m.update(str.encode("utf-8"))
        return m.hexdigest()  # 每次取出用户的uid，然后通过这个加密字符串，判断用户的 cookie 是否改变。

    @staticmethod   # 静态方法
    def genePwd( pwd,salt ):   # 生成登录密码 （根据用户输入的密码，和加密字符串salt）,用 hashlib的md5 和 base64
        m = hashlib.md5()
        str = "%s-%s"%(base64.encodebytes(pwd.encode("utf-8")),salt)  # base64加密 字符串pwd 的字节码 和 秘钥salt， 组合新的参数
        m.update( str.encode("utf-8"))  # 加密，转换为字节码
        return m.hexdigest()  # 返回16进制的编码

    @staticmethod  # 静态方法
    def geneSalt( length=16 ): # 定义 数据库salt字段，即密码加密规则
        #  string所有的ascii + string的数字，组成一个字符串。通过 for i in range(length) 取出16位。
        keylist = [random.choice( (string.ascii_letters + string.digits) ) for i in range(length)]
        return ("".join(keylist))  # 进行拼接

