//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address: null,
        yun_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null
    },
    onShow: function () {
        var that = this;
        this.getOrderInfo();
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params:JSON.parse( e.data )
        });
    },
    //创建订单
    createOrder: function (e) {  // 发送 创建订单网络请求 到后端（data是 发送的信息）
        wx.showLoading();
        var that = this;
        var data = {
            type:this.data.params.type,
            goods:JSON.stringify( this.data.params.goods )
        };

        wx.request({ //用 wx.request()，向后台发送 ajax 网络请求
            url:app.buildUrl('/order/create'),  // 下单方法
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function( res ){  // success：成功的方法体到底是什么
                wx.hideLoading(); // 下完单后，隐藏这个 Loading
                var resp = res.data;
                if( resp.code !=200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }

                wx.navigateTo({  // 下单成功时，才页面跳转（跳到 展示我下单的列表 页面）
                    url: "/pages/my/order_list"
                });

                that.setData({
                    goods_list:resp.data.food_list,   // 后台返回的 结果集
                    default_address:resp.data.default_address,
                    yun_price:resp.data.yun_price,
                    pay_price:resp.data.pay_price,
                    total_price:resp.data.total_price,
                })
            }
        });


    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },
    //提交订单信息
    getOrderInfo:function(){  // 发送 提交订单信息的 网络请求 到后端
        var that = this;
        var data = {
            type:this.data.params.type,
            goods:JSON.stringify( this.data.params.goods )
        };

        wx.request({ //用 wx.request()，向后台发送 ajax 网络请求
            url:app.buildUrl('/order/info'),
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function( res ){  // success：成功的方法体到底是什么
                var resp = res.data;
                if( resp.code !=200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }

                that.setData({
                    goods_list:resp.data.food_list,   // 后台返回的 结果集
                    default_address:resp.data.default_address,
                    yun_price:resp.data.yun_price,
                    pay_price:resp.data.pay_price,
                    total_price:resp.data.total_price,
                })
            }
        });
    }

});
