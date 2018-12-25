;
var account_index_ops = {
  init:function(){
        this.eventBind();
  },
  eventBind:function(){
        var that = this;  // 这时删除恢复调用的同一方法作用域变了。所有重新定义一个
        $(".wrap_search .search").click(function(){  // 直接将这个表单给 submit
            $(".wrap_search").submit();  // 这个是jQuery的方法，可以快速提交。嘿嘿嘿jQuery是个造福人的好东西
        });

        $(".remove").click( function(){  // 如果是删除，需要获得它的点击事件
            that.ops( "remove",$(this).attr("data"));  // act方法remove。id就是当前这个里面的data属性。jQuery获取某个对象的属性通过attr。
        });

        $(".recover").click( function(){  // 恢复数据。删除恢复去其实是一个动作，这里我们点击完了统一调用一个方法。
            that.ops( "recover",$(this).attr("data"));  // act方法recover。id就是当前这个里面的data属性。jQuery获取某个对象的属性通过attr。
        });
  },
  ops:function( act,id ){ // act动作，然后传入的id
        // 直接提交给后端
        var callback = {
          'ok':function(){  // 确认按钮

            $.ajax({
                url:common_ops.buildUrl( "/account/ops" ),  // 统一通过ops的方法，统一处理。ops在后台了
                type:'POST',
                data:{ // data就是传过来的，act和id
                    act:act,  // 表示动作（删除还是恢复）
                    id:id    // 哪条数据
                },
                dataType:'json', // 数据格式
                success:function( res ){
                     var callback = null;
                        if ( res.code == 200 ){
                            callback = function(){
                                window.location.href = window.location.href;  // 200状态下特殊处理，默认刷新当前页面
                            }
                        }
                        common_ops.alert( res.msg,callback );
                }
                });
               },
                'cancel':null // 取消按钮
        };
        // 这个方法是封装好的。common.js将页面url进行统一封装，然后进行二次使用
        common_ops.confirm( ( act == "remove" ? "确定删除？":"确定恢复？"),callback);  //参数 ：callback
   }

};

$(document).ready( function(){
    account_index_ops.init();
} );

//这种方式是按照对象的方式来写。更好的方式有待挖掘。我们可以相互探讨哦1!!
