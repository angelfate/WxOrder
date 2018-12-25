;
var account_set_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".wrap_account_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("请勿重复提交！");
                return;
            }

            var nickname_target = $(".wrap_account_set input[name=nickname]");
            var nickname = nickname_target.val();

            var mobile_target = $(".wrap_account_set input[name=mobile]");
            var mobile = mobile_target.val();

            var email_target = $(".wrap_account_set input[name=email]");
            var email = email_target.val();

            var login_name_target = $(".wrap_account_set input[name=login_name]");
            var login_name = login_name_target.val();

            var login_pwd_target = $(".wrap_account_set input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();

            var login_pwd_2_target = $(".wrap_account_set input[name=login_pwd_2]");
            var login_pwd_2 = login_pwd_target.val();

            var mobile_reg = new RegExp("^(13\\d|14[5|7]|15\\d|166|17[3|6|7]|18\\d)\\d{8}$"); // 手机验证正则表达式
            var email_reg = new RegExp("^([a-zA-Z0-9]+[_|\\_|\\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\\_|\\.]?)*[a-zA-Z0-9]+\\.[a-zA-Z]{2,3}$"); //邮箱验证正则表达式
            var login_name_reg = new RegExp("^[0-9a-zA-Z.@]*$");

            if( !nickname ){
                common_ops.tip( "姓名不能为空!",nickname_target );
                return false;
            }else if( nickname.length < 2 || nickname.length > 15 ){
                common_ops.tip( "请输入符合规范的姓名!",nickname_target );
                return false;
            }

            if( !mobile ){
                common_ops.tip( "手机号码不能为空!",mobile_target );
                return false;
            }else if( !mobile_reg.test(mobile)){
                common_ops.tip( "请输入符合规范的手机号!",mobile_target );
                return false;
            }

            if( !email ){
                common_ops.tip( "邮箱不能为空!",email_target );
                return false;
            }else if( !email_reg.test(email)){
                common_ops.tip( "请输入符合规范的邮箱!",email_target );
                return false;
            }

             if( !login_name ){
                common_ops.tip( "登录用户名不能为空!",login_name_target );
                return false;
            }else if( login_name.length < 2 || login_name.length > 15 ){
                common_ops.tip( "请输入符合规范的登录用户名!",login_name_target );
                return false;
            }else if( !login_name_reg.test(login_name)){
                common_ops.tip( "登录名只能包含数字、字母、‘.’、‘@’!",login_name_target );
                return false;
            }

            if( !login_pwd ){
                common_ops.tip( "登录密码不能为空!",login_pwd_target );
                return false;
            }else if( login_pwd.length < 6 || login_pwd.length > 16 ){
                common_ops.tip( "请输入符合规范的登录密码!",login_pwd_target );
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                nickname: nickname,
                mobile: mobile,
                email: email,
                login_name:login_name,
                login_pwd:login_pwd,
                id:$(".wrap_account_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl( "/account/set" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = common_ops.buildUrl("/account/index");
                        }
                    }
                    common_ops.alert( res.msg,callback );
                }
            });


        });
    }
};

$(document).ready( function(){
    account_set_ops.init();
} );