;  //分号  因为当作很多系统时，会有压缩软件，UI吧多个js文件压缩到一起。；用来进行分割。
var user_login_ops = {
    init:function(){  //
        this.eventBind()   //调用下面的eventBind方法
    },

    eventBind:function(){  // 事件绑定方法。点击‘确认提交’按钮后
        $(".login_warp .do-login").click( function(){//login_warp下面的 do-login，点击事件

            var btn_target = $(this); // 定义 btn_target，监听当前状态

            if( btn_target.hasClass( "disabled" )){ //防止用户重复提交。如果当前页面有一个disabled
                common_ops.alert( "请勿重复提交！" )
                return;
            }

            var login_name = $(".login_warp input[name=login_name]").val();// jQuery写法。获取用户名
            var login_pwd = $(".login_warp input[name=login_pwd]").val();

            if( login_name == undefined || login_name.length<2 ){// 如果登录名为空
                common_ops.alert("请输入正确的登录用户名!");  // common_ops 是common.js里面封装好的
                return;
            }

             if( !login_pwd || login_pwd.length<6 ){ //
                common_ops.alert("请输入正确的登录名和密码!");  // common_ops 是common.js里面封装好的
                return;
            }

            btn_target.addClass( "disabled" );  // 判断完成时，添加 disabled
            //return;
            $.ajax({  // 判断完成说明都是合法的，进行 ajax提交
                url:common_ops.buildUrl("/user/login"),    // 提交到这里
                type:"POST",  //方式
                data:{ 'login_name':login_name,'login_pwd':login_pwd },
                dataType:'json',
                success:function( res ){  //success用的是jQuery ajax的语法
                    //登录成功，跳转到首页
                    btn_target.removeClass("disabled");  // 当请求回来之后，进行移除 class
                    var callback = null;
                    if ( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/");
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });

        });
    }
};

$(document).ready( function(){   // jQuery方法。当页面加载之后，要执行
    user_login_ops.init();
});