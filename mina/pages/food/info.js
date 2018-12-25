//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
var utils = require('../../utils/util.js');  // 在这里引入要用到的 js

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax:1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount:2
    },
    onLoad: function ( e ) {
        var that = this;

        that.setData({  // 设置值。获取 e对象 的 id值
            id:e.id
        });

        that.setData({
            commentList: [
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                },
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                }
            ]
        });
    },
    onShow:function(){  // 页面进行显示时，就调用这个方法（基于事件的驱动）
        this.getInfo();
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    addShopCar: function () {  // 添加购物车（想后端发送一个 ajax请求）
        var that = this;
        var data = {
            "id":this.data.info.id,  // 商品id
            "number":this.data.buyNumber,   // 前台绑定的 buyNumber,即用户输入的数量
        };
         wx.request({  // 发送网络请求
            url:app.buildUrl("/cart/set"),  // 设置一个 car 的set方法，设置购物车数量
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function( res ){
                var resp = res.data;  // 真正的用户返回值
                app.alert({ 'content':resp.msg }); // 如果是否成功，都会弹出窗口信息
                that.setData({  // 添加完成之后，规格选择弹出框隐藏起来
                    hideShopPopup:true
                });
            }
        });
    },
    buyNow: function () {  // 立即购买
        wx.navigateTo({
            url: "/pages/order/index"
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if( this.data.buyNumber <= this.data.buyNumMin){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if( this.data.buyNumber >= this.data.buyNumMax ){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    getInfo:function(){ // 来获取详情数据
        var that = this; // 发送请求之前获得id值（这么写，是因为js有作用域。this代表当前这个对象。网络请求时作用域会变）
        wx.request({
            url:app.buildUrl("/food/info"),  // 发送请求到info
            header:app.getRequestHeader(),
            data:{
                id:that.data.id
            },
            success:function( res ){
                var resp = res.data; // 官方的方法，获得 data数据，即后台返回的参数
                if( resp.code != 200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }

                that.setData({
                    info:resp.data.info,
                    buyNumMax:resp.data.info.stock,   // 最大购买数量
                    shopCarNum:resp.data.cart_number,  // 购物车数量
                });
                WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);
            }
        });
    },
    onShareAppMessage:function() {  // 官方 分享页面方法。加载这个方法，然后返回下面json对象，实现转发
        var that = this;  // 怕作用域变化
        return {
            title: that.data.info.name,
            path: '/page/food/info?id=' + that.data.info.id,
            success:function( res ){
                // 转发成功
                wx.request({  // 想后端发送请求。用来记录转发信息
                    url:app.buildUrl("/member/share"),  // 发送请求到/member/share
                    header:app.getRequestHeader(),
                    method:'POST',  // 此时请求的方法换成，POST。因为要写入数据
                    data:{
                        url:utils.getCurrentPageUrlWithArgs()    // 小程序获取当前页面url，百度很多方法。这里的方法是utils下面封装好的
                    },
                    success:function( res ){
                    }
                });
            },
            fail:function( res ){
                // 转发失败
            }
        }
    }
});
