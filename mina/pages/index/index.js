//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    regFlag:true, // 判断是否授权,默认已经注册
  },
  goToIndex:function(){
    wx.switchTab({
      url: '/pages/food/index',
    });
  },
  onLoad:function(){
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    this.checkLogin(); //onLoad 时，就调用登录验证
  },
  onShow:function(){

  },
  onReady: function(){
    var that = this;
    setTimeout(function(){
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function(res) {
      var angle = -(res.x*30).toFixed(1);
      if(angle>14){ angle=14; }
      else if(angle<-14){ angle=-14; }
      if(that.data.angle !== angle){
        that.setData({
          angle: angle
        });
      }
    });
  },
  checkLogin:function(){  // 验证登录，判断是否已经登录过，通过code
    var that = this; // 选择的路的按钮 button
    wx.login({
        success:function( res ){  // 如果成功了
            if ( !res.code ) { // 如果没有code信息
              //发起网络请求
              app.alert( { 'content':'登录失败，请重新登录' } );
              return;  // 统一返回
            }
            wx.request({ //用 wx.request()，向后台发送 ajax 请求
                url:app.buildUrl('/member/check-reg'),
                header:app.getRequestHeader(),
                method:'POST',
                data:{ 'code':res.code}, // 返回给后台code
                success:function( res ){  // success：成功的方法体到底是什么
                    if( res.data.code !=200 ){  // 如果没有绑定信息时，后台给的code不是200。注意res.data.code 才是服务器返回的信息
                        that.setData({ //这是wx的一个方法
                            regFlag:false // 判断是否授权,flase没有注册（新用户没有授权过）
                        });
                        return; // 没有登录时就这样显示
                    }
                    app.setCache( "token",res.data.data.token ) // key值是token。值是 res.data.data(返回值),它里面有token值
                    that.goToIndex(); // 登录成功的话，进入到首页
                }
        });
        }
    });
  },

  login:function( e ){  //登录方法
    var that = this;
//    console.log(e.detail.encryptedData)
    if( !e.detail.userInfo ){ // 如果没有用户信息
        app.alert( { 'content':'登录失败，请重新登录' } );
        return;  // 统一返回
    }


    var data = e.detail.userInfo; // 如果有用户信息，就传给后台
    wx.login({
      success (res) {
        if ( !res.code ) { // 如果没有code信息
          //发起网络请求
          app.alert( { 'content':'登录失败，请重新登录' } );
          return;  // 统一返回
        }
        data['code'] = res.code;
        wx.request({ //用 wx.request()，向后台发送 ajax 请求
            url:app.buildUrl('/member/login'),
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function( res ){  // success：成功的方法体到底是什么
                if( res.data.code !=200 ){ // 后台给的code不是200，即注册失败。注意res.data.code 才是服务器返回的信息
                    app.alert( { 'content':res.msg });
                    return;
                }
                app.setCache( "token",res.data.data.token ) // key值是token。值是 res.data.data(返回值),它里面有token值
                that.goToIndex(); // 登录成功的话，进入到首页
            }
        });
      }
    });
  }
});