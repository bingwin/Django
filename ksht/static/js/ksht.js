/**
 * Created by Administrator on 2017/2/7.
 * var 1.0.0
 */



function getFormJson(form) {
    var o = {};
    var a = $(form).serializeArray();
    $.each(a, function () {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;

}


function webp2jpg(_url) {
    if (_url.indexOf(".webp?") == -1) {
        var url = _url;
        url = url.substring(0, url.indexOf(".webp?"));
        if (url.substring(url.length - 4) == "_low") {
            url = url.substring(0, url.length - 5)
        }
        url = url + ".jpg";
        return url
    } else {
        return _url
    }

}


function dbts() {

    $.modal({
        title: '<i class="weui-icon-warn"></i>警告',
        text: '您正在使用盗版应用。请及时删除盗版应用以防被盗号等不必要的损失。<br>我们的唯一网站是ksht.3agzs.com',
        buttons: [
            {
                text: "下载正版应用", className: "default", onClick: function () {
                self.location = 'http://ksht.oss-cn-hangzhou.aliyuncs.com/download/0f9b83c1650a907138533adcba4ea5bd.apk';

                dbts();
            }
            }
        ]
    });


}

appkefu = false;
function kefu_init_(appVersion) {

    if (isappuser && compare(appVersion, "1.2.2")) {
        appkefu = true;


    } else {
        appkefu = false;
        (function (m, ei, q, i, a, j, s) {
            m[i] = m[i] || function () {
                (m[i].a = m[i].a || []).push(arguments)
            };
            j = ei.createElement(q),
                s = ei.getElementsByTagName(q)[0];
            j.async = true;
            j.charset = 'UTF-8';
            j.src = 'https://static.meiqia.com/dist/meiqia.js?_=t';
            s.parentNode.insertBefore(j, s);
        })(window, document, 'script', '_MEIQIA');
        _MEIQIA('entId', 80922);
        _MEIQIA('withoutBtn');



    }

}

function kefu_init() {
    if (isappuser && !isInclude("script/api.js")) {
        document.write('<script type=\"text/javascript\" src=\"' + static_url + 'js/api.js\"></script>');
    }

    if (isappuser) {
        apiready = function () {
            kefu_init_(api.appVersion);
        }
    } else {
        kefu_init_("0.0.0");
    }


}

function kefu_open() {
    //;
    if (appkefu) {
        api.execScript({name: 'root', script: 'qiyuSdk.openServiceWindow({sessionTitle:\'联盟客服\',});'});
    } else {
        _MEIQIA('showPanel');

    }
}


function isInclude(name) {
    var js = /js$/i.test(name);
    var es = document.getElementsByTagName(js ? 'script' : 'link');
    for (var i = 0; i < es.length; i++)
        if (es[i][js ? 'src' : 'href'].indexOf(name) != -1) return true;
    return false;
}

/*
 * 版本号比较方法
 * 传入两个字符串，当前版本号：curV；比较版本号：reqV
 * 调用方法举例：compare("1.1","1.2")，将返回false
 */
function compare(curV, reqV) {
    if (curV && reqV) {
        //将两个版本号拆成数字
        var arr1 = curV.split('.'),
            arr2 = reqV.split('.');
        var minLength = Math.min(arr1.length, arr2.length),
            position = 0,
            diff = 0;
        //依次比较版本号每一位大小，当对比得出结果后跳出循环（后文有简单介绍）
        while (position < minLength && ((diff = parseInt(arr1[position]) - parseInt(arr2[position])) == 0)) {
            position++;
        }
        diff = (diff != 0) ? diff : (arr1.length - arr2.length);
        //若curV大于reqV，则返回true
        return diff > 0;
    } else {
        //输入为空
        console.log("版本号不能为空");
        return false;
    }
}