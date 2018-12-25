;
var member_set_ops = {
    init:function(){
        this.eventBind();
    },
    eventBind:function(){
        $(".wrap_member_set .save").click(function(){
            var btn_target = $(this);
            if( btn_target.hasClass("disabled") ){
                common_ops.alert("请勿重复提交！");
                return;
            }

            var nickname_target = $(".wrap_member_set input[name=nickname]");
            var nickname = nickname_target.val();


            if( !nickname ){
                common_ops.tip( "姓名不能为空!",nickname_target );
                return false;
            }else if( nickname.length < 2 || nickname.length > 15 ){
                common_ops.tip( "请输入符合规范的姓名!",nickname_target );
                return false;
            }

            btn_target.addClass("disabled");

            var data = {
                nickname: nickname,
                id:$(".wrap_member_set input[name=id]").val()  // 取出页面的隐藏值id。返给后台
            };

            $.ajax({
                url:common_ops.buildUrl( "/member/set" ),
                type:'POST',
                data:data,
                dataType:'json',
                success:function( res ){
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if( res.code == 200 ){
                        callback = function(){
                            window.location.href = window.location.href;
                        }
                    }
                    common_ops.alert( res.msg,callback ); // callback上面定义的方法，默认不处理
                }
            });


        });
    }
};

$(document).ready( function(){
    member_set_ops.init();
} );

// 所有的数据通过 js验证过后，由ajax方法提交给后端验证