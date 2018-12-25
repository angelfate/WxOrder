__author__ = '未昔'
__date__ = '2018/11/21 19:46'

from application import app,manager
from flask_script import Server  # 为了支持 main() 里面的写法,将app.run()改成 manager.run()
import www

##web server   可以自定义命令
manager.add_command( "runserver", Server( host='0.0.0.0',port=app.config['SERVER_PORT'],use_debugger=True,use_reloader=True) )


def main():
    manager.run()


if __name__ == '__main__':
    try:
        import sys
        sys.exit( main() )  # 返回状态值，执行mian方法
    except Exception as e:
        import traceback
        traceback.print_exc()  # 输出错误
