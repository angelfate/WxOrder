//app.js
App({
    onLaunch: function () {
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "鲤跃龙门在线外卖",
        domain:"http://127.0.0.1:8999/api"
    },
    tip:function( params ){
        var that = this;
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            success: function(res) {

                if ( res.confirm ) {//点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{//点击否
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    alert:function( params ){
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            showCancel:false,
            success: function(res) {
                if (res.confirm) {//用户点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console:function( msg ){
        console.log( msg);
    },
    getRequestHeader:function(){
        return {
            'content-type': 'application/x-www-form-urlencoded',  // 因为默认的header是json，所以我们要这么获取
            'Authorization': this.getCache("token"), // 获得token,传回前端。方便解析token，判断用户
        }
    },
    buildUrl:function( path,params ){
        var url = this.globalData.domain + path;  // 空是留给 domain的，也可以写死(不推荐)
        var _paramUrl = "";
        if ( params ){

            _paramUrl = Object.keys( params ).map( function( k ){  // 定义的params是一个json，可以取它的keys。进行map的循环，循环的方法 k

                return [ encodeURIComponent( k ),encodeURIComponent( params[ k ] )].join("=");  // encodeURIComponent 将k 进行转译，然后对应的值params[ k ]，即k的value。用 = 连接

                // return 的是一个字符串。最终结果类似于 a=b&c=d
            }).join("&");  // 因为返回的还是一个数组，所有进行json

            _paramUrl = "?" + _paramUrl
        }
        return url + _paramUrl;  // 最终的 返回
    },
    getCache:function( key ){  // 数据缓存
        var value = undefined;// 默认值空
        try {
            value = wx.getStorageSync(key)
        } catch (e) {
    // Do something when catch error
        }
        return value; /// 如果没有 就返回上面的空
    },
    setCache:function( key,value ){  // 将数据存储到本地当中（这里我采用了 异步）
        wx.setStorage({
          key:key,
          data:value
        });
    }
});