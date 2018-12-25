__author__ = '未昔'
__date__ = '2018/12/5 14:06'
from application import app
from common.libs.Helper import ops_render   # 返回自定义页面
from common.libs.LogService import LogService


@app.errorhandler( 404 )  ## 驳货 404 的错误
def error_404( e ):
    LogService.addErrorLog( str(e) ) # 字符串方式
    return ops_render( 'error/error.html',{ 'status':404,'msg':'很抱歉，您访问的页面不存在！' } )

@app.errorhandler( 500 )  ## 驳货 404 的错误
def error_500( e ):
    return ops_render( 'error/error.html',{ 'status':500,'msg':'很抱歉，服务内部异常！' } )

@app.errorhandler( 502 )  ## 驳货 404 的错误
def error_500( e ):
    return ops_render( 'error/error.html',{ 'status':502,'msg':'Sorry，Bad Gateway！' } )
