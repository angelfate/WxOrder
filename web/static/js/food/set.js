;
var upload = { // 上传的事件
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) { // 拼接 封面图url，然后把图片放在‘封面图’旁边
        if (!file_key) {
            return;
        }
            var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';  // 拼接url

        if ($(".upload_pic_wrap .pic-each").size() > 0) { // 入股偶没有图片，就增加一条下面数据
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        food_set_ops.delete_img();
    }
};

var food_set_ops = {
    init:function(){
        this.ue = null;
        this.eventBind();
        this.initEditor();
        this.delete_img();
    },
    eventBind:function(){ // 下面两个插件，可以直接百度 jquery
        var that = this;

        $(".wrap_food_set .upload_pic_wrap input[name=pic]").change(function(){ // upload_pic_wrap input[name=pic]元素表示符。change事件，说明变化了
            $(".wrap_food_set .upload_pic_wrap").submit();   // 自动提交这个表单。为什么用form，因为form有submit事件
        });

        $(".wrap_food_set select[name=cat_id]").select2({  // 分类下拉菜单。在wrap_food_set下面，获取select的name=cat_id，然后绑定select2事件。
            language:'zh-CN',
            width:'100%',
        });

         $(".wrap_food_set input[name=tags]").tagsInput({  // 标签，绑定tagsInput事件。（所有只要有name就可以调用）
            width:'auto',
            height:40,
            'defaultText':'添加标签', //默认文字
            'placeholderColor':'green', //设置defaultText的颜色
            'maxChars':8, //每个标签的最大字符，如果不设置或者为0，就是无限大
            onAddTag: function (tag) {
            },
            onRemoveTag: function (tag) {
            }
        });

         $(".wrap_food_set .save").click(function () {  // 美食页面提交的ajax验证
            var btn_target = $(this);
                if (btn_target.hasClass("disabled")) {  // 按钮的处理
                    common_ops.alert("正在处理!!请不要重复提交~~");
                    return;
                }

            var cat_id_target = $(".wrap_food_set select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".wrap_food_set input[name=name]");
            var name = name_target.val();

            var price_target = $(".wrap_food_set input[name=price]"); // 价格
            var price = price_target.val();

            var summary = $.trim(that.ue.getContent());  // 描述。that.ue是initEditor方法定义的

            var stock_target = $(".wrap_food_set input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".wrap_food_set input[name=tags]");
            var tags = $.trim(tags_target.val());

            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }

            if (name.length < 1) {
                common_ops.alert("请输入符合规范的名称~~");
                return;
            }

            if (parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            if ($(".wrap_food_set .pic-each").size() < 1) {
                common_ops.alert("请上传封面图~~");
                return;
            }

            if (summary.length < 10) {
                common_ops.tip("请输入描述，并不能少于10个字符~~", price_target);
                return;
            }

            if (parseInt(stock) < 1) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }else if ( stock % 1 !=0 ) {
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }

            if (tags.length < 1) {
                common_ops.alert("请输入标签，便于搜索~~");
                return;
            }

            btn_target.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                price: price,
                main_image: $(".wrap_food_set .pic-each .del_image").attr("data"),
                summary: summary,
                stock: stock,
                tags: tags,
                id: $(".wrap_food_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("/food/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/food/index");
                        }
                    }
                    common_ops.alert(res.msg, callback);
                }
            });

        });
    },

    initEditor:function(){  // 专门做 initEditor 的初始化
        var that = this; // 防止作用域改变（当使用function时，作用域就变了）
        that.ue =  UE.getEditor('editor',{ // json参数自定义
            toolbars: [
                ['undo', 'redo', '|',
                    'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', '|', 'rowspacingtop', 'rowspacingbottom', 'lineheight'],
                ['customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                    'directionalityltr', 'directionalityrtl', 'indent', '|',
                    'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                    'link', 'unlink'],
                ['imagenone','imageleft', 'imageright', 'imagecenter', '|',
                     'simpleupload','insertimage', 'insertvideo', '|',
                    'horizontal', 'spechars', '|', 'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols','|','edittip','scrawl','emotion' ]

            ],
            enableAutoSave: true, // 自动保存
            saveInterval: 60000,  // 保存时间
//            //lementPathEnabled: true; // 元素路径
//            allHtmlEnabled:false; //提交到后台的数据是否包含整个html字符串
            maximumWords:20000, //允许的最大字符数
            zIndex:4, // 顶部高度 默认900
            serverUrl:common_ops.buildUrl("/upload/ueditor") // 上传
        }); // this变了时，直接同用that就行了

    },
    delete_img:function(){
        $(".wrap_food_set .del_image").unbind().click( function(){// del_image是上面拼接url时加的
            $(this).parent().remove();  // 父类进行移除
        });
    }

};

$(document).ready( function(){
    food_set_ops.init();
});