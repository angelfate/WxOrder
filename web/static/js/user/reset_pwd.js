;
var mod_pwd_pops = {  // 操作两步式init，eventBind
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        // 事件绑定过程
        $("#save").click( function() {  // #save，是因为保存时用的save 是一个id。id是唯一的。

            var btn_target = $(this); // 定义 btn_target，监听当前状态

            if( btn_target.hasClass( "disabled" )){ // 参烤 login.js
                common_ops.alert( "请勿重复提交！" )
                return;
            }

            // 获取要传递的变量
            var old_password = $("#old_password").val();
            var new_password = $("#new_password").val();
            var new_password2 = $("#new_password2").val();


            if( !old_password ){
                common_ops.alert( "请输入原密码！",old_password );  // 换个方式，用alert，弹出窗口信息
                return false;  // 终止提交
            }else if( old_password.length<6 ){
                common_ops.alert( "原密码错误！" );
                return false;  // 终止提交
            }

            if( !new_password || new_password.length<6 ){
                common_ops.alert( "请输入不少于6位的新密码！",new_password );
                return false;  // 终止提交
            }else if( new_password.length>15 ){
                common_ops.alert( "请输入不超过15位的新密码！",new_password );
                return false;  // 终止提交
            }

            if( new_password==old_password ){
                common_ops.alert( "新密码与原密码不能相同！",new_password );
                return false;  // 终止提交
            }

            if( !new_password2 ){
                common_ops.alert( "请重新输入新密码！",new_password2 );  // 换个方式，用alert，弹出窗口信息
                return false;  // 终止提交
            }else if( new_password2!= new_password ){
                common_ops.alert( "两次密码不一致！",new_password2 );
                return false;  // 终止提交
            }

            btn_target.addClass("disabled");  // 参数验证完成时，添加这个,防止重复提交。

            var data = {  // 传递到后端
                old_password : old_password,
                new_password : new_password,
            };

            $.ajax({
                url:common_ops.buildUrl( "/user/reset-pwd" ),  // 提交到这里
                type:'POST',
                data:data,
                dataType:'json', // 数据格式
                success:function( res ){
                     //登录成功，跳转到首页
                    btn_target.removeClass("disabled");  // 当请求回来之后，进行移除 class
                    var callback = null;
                    if ( res.code == 200 ){
                        callback = function(){
                            window.location.href = window.location.href;  // 200状态下特殊处理，默认刷新当前页面
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });

        })
    }

};

$(document).ready( function(){  // jQuery 加载完成时，执行
    mod_pwd_pops.init();      // jQuery的使用方法。然后json去写对象。产生类的用法
})