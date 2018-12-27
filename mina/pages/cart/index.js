//index.js
var app = getApp();
Page({
    data: {},
    onLoad: function () {
        //this.getCartList();
    },
    onShow:function(){  // 定义显示的方法，这个方法会去后端获取数据
        this.getCartList();
    },
    //每项前面的选中框
    selectTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (index !== "" && index != null) {
            list[ parseInt(index) ].active = !list[ parseInt(index) ].active;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //计算是否全选了
    allSelect: function () {
        var list = this.data.list;
        var allSelect = false;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (curItem.active) {
                allSelect = true;
            } else {
                allSelect = false;
                break;
            }
        }
        return allSelect;
    },
    //计算是否都没有选
    noSelect: function () {
        var list = this.data.list;
        var noSelect = 0;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (!curItem.active) {
                noSelect++;
            }
        }
        if (noSelect == list.length) {
            return true;
        } else {
            return false;
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        var currentAllSelect = this.data.allSelect;
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            list[i].active = !currentAllSelect;
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
    },
    //加数量
    jiaBtnTap: function (e) {
        var that = this;
        var index = e.currentTarget.dataset.index;
        var list = that.data.list;
        list[parseInt(index)].number++;
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
        this.setCart( list[parseInt(index)].food_id,list[parseInt(index)].number )
    },
    //减数量
    jianBtnTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (list[parseInt(index)].number > 1) {
            list[parseInt(index)].number--;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
            this.setCart( list[parseInt(index)].food_id,list[parseInt(index)].number )
        }
    },
    //编辑默认全不选
    editTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = false;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    //选中完成默认全选
    saveTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = true;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    getSaveHide: function () {
        return this.data.saveHidden;
    },
    totalPrice: function () {
        var list = this.data.list;
        var totalPrice = 0.00;
        for (var i = 0; i < list.length; i++) {
            if ( !list[i].active) {
                continue;
            }
            totalPrice = totalPrice + parseFloat( list[i].price ) * list[i].number;
        }
        return totalPrice;
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        this.setData({
            list: list,
            saveHidden: saveHidden,
            totalPrice: total,
            allSelect: allSelect,
            noSelect: noSelect,
        });
    },
    //去结算
    toPayOrder: function () {
        var data = {  // 传一个 json给后台，小程序里面json方便
            type:"cart",
            goods:[]
        };

        var list = this.data.list; // 下单的商品是所有选中的商品
        for(var i=0;i<list.length;i++){
            if( !list[i].active ){// 如果商品下标没有选中就是不要的。
                continue;
            }
            data['goods'].push({// 添加商品,json
                "id":list[i].food_id,
                "price":list[i].price,
                "number":list[i].number,
            });
        }

        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify( data )  // 传一个 json数据 给后端，进行解析
        });
    },
    //如果没有显示去光光按钮事件
    toIndexPage: function () {
        wx.switchTab({
            url: "/pages/food/index"
        });
    },
   //选中删除的数据
    deleteSelected: function () {  // 选中删除事件
        var list = this.data.list;
        var goods = [];
        list = list.filter(function ( item ) {
            if( item.active ){ // 如果被选中
                goods.push({
                    "id":item.food_id  // 商品id
                });
            }
            return !item.active;
        });
        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        //发送请求到后台删除数据
        wx.request({  // 向后端发送网络请求，取获得后端返回的数据。拿来个前台显示
            url:app.buildUrl("/cart/del"),  // 这个方法在 app.js已经统一分装好了
            header:app.getRequestHeader(),
            method:'POST',
            data:{
                goods:JSON.stringify( goods )  // 传递json，给后端解析
            },
            success:function( res ){
                var resp = res.data;  // 真正的用户返回值
                app.alert({ 'content':resp.msg }); // 如果是否成功，都会弹出窗口信息

                //that.setData({  // 添加完成之后，规格选择弹出框隐藏起来
                //   hideShopPopup:true
                //});
            }
        });
    },
    getCartList: function () {
        var that = this;  // 防治作用域变化

         wx.request({  // 向后端发送网络请求，取获得后端返回的数据。拿来个前台显示
            url:app.buildUrl("/cart/index"),  // 这个方法在 app.js已经统一分装好了
            header:app.getRequestHeader(),
            success:function( res ){
                var resp = res.data; // 官方的方法
                if( resp.code != 200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }
                that.setData({
                    list:resp.data.list,
                    saveHidden: true,
                    totalPrice: "0.00",  // 总价格
                    allSelect: true,  // 是否全选中
                    noSelect: false,   // 不选中
                });

                // 调用方法，进行统一渲染。因为网络请求时异步的。此时的this换成that，因为作用域变了
                that.setPageData( that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list);
            }
        });
    },
    setCart:function( food_id,number ){  // 统一提交到后端的方法
        var that = this;
        var data = {
            "id":food_id,  // 商品id
            "number":number,   // 前台绑定的 buyNumber,即用户输入的数量
        };
         wx.request({  // 发送网络请求
            url:app.buildUrl("/cart/set"),  // 设置一个 car 的set方法，设置购物车数量
            header:app.getRequestHeader(),
            method:'POST',
            data:data,
            success:function( res ){  // 这里就不弹出，购物车改变的信息了。

            }
        });
    }
});
