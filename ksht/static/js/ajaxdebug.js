/**
 * Created by Administrator on 2017/2/7.
 */
(function ($) {
    //首先备份下jquery的ajax方法


    //重写jquery的ajax方法
    $.ajax = function (url,options) {
        if ( typeof url === "object" ) {
            options = url;
            url = undefined;
        }
        if (options.url == "user/register"){
            options.success({"err":0,"msg":"阿斯顿阿斯顿阿斯顿","url":"wo.html"})
        }

        return null ;
    };
})(jQuery);
