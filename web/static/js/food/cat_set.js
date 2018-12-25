;
var food_cat_set_pops = {  // 操作两步式init，eventBind
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        // 事件绑定过程
        $(".wrap_cat_set .save").click( function() {  // #save，是因为保存时用的save 是一个id。id是唯一的。

            var btn_target = $(this); // 定义 btn_target，监听当前状态

            if( btn_target.hasClass( "disabled" )){ // 参烤 login.js
                common_ops.alert( "请勿重复提交！" )
                return;
            }

            // 获取要传递的变量
            var name_target = $(".wrap_cat_set input[name=name]")
            var name = name_target.val();

            var weight_target = $(".wrap_cat_set input[name=weight]")
            var weight = weight_target.val();

            if( !name ){
                common_ops.tip( "分类名称不能为空！",name_target );  // 换个方式，用alert，弹出窗口信息
                return false;  // 终止提交
            }else if( name.length<2 || name.length>12 ){
                common_ops.tip( "请输入符合规范的分类名称！",name_target );
                return false;  // 终止提交
            }

            if( !weight ){
                common_ops.tip( "权重不能为空！",weight_target );  // 换个方式，用alert，弹出窗口信息
                return false;  // 终止提交
            }else if( parseInt(weight)<1 ){
                common_ops.tip( "请输入符合规范的权重，并且大于0！",weight_target );
                return false;  // 终止提交
            }

            btn_target.addClass("disabled");  // 参数验证完成时，添加这个,防止重复提交。

            var data = {  // 传递到后端
                name : name,
                weight : weight,
                id:$(".wrap_cat_set input[name=id]").val()  // 取出页面的隐藏值id。返给后台
            };

            $.ajax({
                url:common_ops.buildUrl( "/food/cat-set" ),  // 提交到这里
                type:'POST',
                data:data,
                dataType:'json', // 数据格式
                success:function( res ){
                     //登录成功，跳转到首页
                    btn_target.removeClass("disabled");  // 当请求回来之后，进行移除 class
                    var callback = null;
                    if ( res.code == 200 ){
                        callback = function(){
                            window.location.href =common_ops.buildUrl("/food/cat");;  // 200状态下特殊处理，默认刷新当前页面
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });

        })
    }

};

$(document).ready( function(){  // jQuery 加载完成时，执行
    food_cat_set_pops.init();      // jQuery的使用方法。然后json去写对象。产生类的用法
})