//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        p:1,  // 页数
        processing:false   // 是否正在才处理，如果正在处理就不能发送请求
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

        this.getBannerAndCat();  // 调用这个方法
    },
    onShow:function(){  // 页面进行显示时，就调用这个方法（基于事件的驱动）
        this.getBannerAndCat();  // 调用这个方法
    },

    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
	listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	 },
	 toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	},
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat:function(){  // 只要发送一个网络请求到后端就行了
        var that = this;
        wx.request({
            url:app.buildUrl("/food/index"),  // 这个方法在 app.js已经统一分装好了
            header:app.getRequestHeader(),
            success:function( res ){
                var resp = res.data; // 官方的方法
                if( resp.code != 200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }
                that.setData({ // 官方方法。将数据统一设置进去
                    banners : resp.data.banner_list,  // 重新改变上面的 数据。
                    categories : resp.data.cat_list,
                });
                 that.getFoodList();  // 首页获取完时，进行一次查询
            }
        });
    },
    catClick:function( e ){  // 首页index.wxml分类的地方，加上 bindtap="catClick"
        //每次选择分类时，设置它的选中值
        this.setData({
            activeCategoryId:e.currentTarget.id,   // 这个id就是前台<view id="{{item.id}}" 绑定的对象
            // 每次分类之前的操作
            p:1,
            goods:[],
            loadingMoreHidden:true, //表示此时是重新进行加载
        });
        this.getFoodList();  // 执行搜索事件
    },
    onReachBottom:function(){ // 上拉刷新，官方方法
        var that = this;
        setTimeout(  function(){  // 下拉到底部时，延时处理，0.5秒，发送请求。
            that.getFoodList();
        },500);
    },
    getFoodList:function(){
        var that = this;
        if( that.data.processing ){  // 如果processing为true。表示正在发生请求或者混蛋没有数据时，不在发送请求
            return;
        }

        if ( !that.data.loadingMoreHidden ){  // 如果为 false说明没有数据了，统一返回就行了
            //app.console("2");  // 打印，调试
            return;
        }

        that.setData({
            processing:true
        });


        wx.request({
            url:app.buildUrl("/food/search"),  // 发送请求到search
            header:app.getRequestHeader(),
            data:{
                cat_id:that.data.activeCategoryId, // 分类id
                mix_kw:that.data.searchInput,  // 搜索框的值
                p:that.data.p,  // 每次请求完将页数重新处理，表示当前页数
            },
            success:function( res ){
                var resp = res.data; // 官方的方法
                if( resp.code != 200 ){
                    app.alert( {"content":resp.msg } );
                    return;
                }
                var goods = resp.data.list;  // 拿到数据
                that.setData({// 填充进去
                    goods:that.data.goods.concat( goods ),  // 实现加载。刷新增加菜品，而不是覆盖
                    p:that.data.p + 1, // 每次处理完时，将p页数 +1
                    processing:false,  // 处理完后，把 这个 设置为 false。说明本次请求完成，可以发送二次请求
               });
               if ( resp.data.has_more == 0){  // 后台的逻辑，说明没有数据了
                    that.setData({
                        loadingMoreHidden:false  // 将它设置为 false
                    });
               }
            }
        });
    }

});
