;
var user_edit_ops = {  // 操作两步式init，eventBind
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        // 事件绑定过程
        $(" .user_edit_wrap .save").click( function() {  // click方法，执行的是事件

            var btn_target = $(this); // 定义 btn_target，监听当前状态

            if( btn_target.hasClass( "disabled" )){ // 参烤 login.js
                common_ops.alert( "请勿重复提交！" )
                return;
            }

            // 获取要传递的变量
            var nickname_target = $(".user_edit_wrap input[name=nickname]");
            var nickname = nickname_target.val(); // nickname = 上面的值

            var email_target = $(".user_edit_wrap input[name=email]");
            var email = email_target.val(); // nickname = 上面的值

            var mobile_target = $(".user_edit_wrap input[name=mobile]");
            var mobile = mobile_target.val();

            var mobile_reg = new RegExp("^(13\\d|14[5|7]|15\\d|166|17[3|6|7]|18\\d)\\d{8}$"); // 手机验证正则表达式
            var email_reg = new RegExp("^([a-zA-Z0-9]+[_|\\_|\\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\\_|\\.]?)*[a-zA-Z0-9]+\\.[a-zA-Z]{2,3}$"); //邮箱验证正则表达式

            if( !nickname || nickname.length <2 ){
                common_ops.tip( "请输入符合规范的姓名！",nickname_target );  // tip是common.js里面封装的方法。（提示的字符串，给哪个元素提示）
                return false;  // 终止提交
            }

             if( !mobile ){
                common_ops.tip( "手机号不能为空！",mobile_target );  // tip是common.js里面封装的方法。（提示的字符串，给哪个元素提示）
                return false;  // 终止提交
            }else if( !mobile_reg.test(mobile)){  // 正则验证不通过
                common_ops.tip( "请输入符合规范的手机号！",mobile_target );
                return false;  // 终止提交
            }

            if( !email ){
                common_ops.tip( "邮箱不能为空！",email_target );  // tip是common.js里面封装的方法。（提示的字符串，给哪个元素提示）
                return false;  // 终止提交
            }else if( !email_reg.test(email)){  // 正则验证不通过
                common_ops.tip( "请输入符合规范的邮箱！",email_target );
                return false;  // 终止提交
            }

            btn_target.addClass("disabled");  // 参数验证完成时，添加这个,防止重复提交。

            var data = {  // json（key,value）
                nickname : nickname,
                email:email,
                mobile:mobile,
            };

            $.ajax({
                url:common_ops.buildUrl( "/user/edit" ),  // 提交到这里
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

        });
    }

};

$(document).ready( function(){  // jQuery 加载完成时，执行
    user_edit_ops.init();      // jQuery的使用方法。然后json去写对象。产生类的用法
});