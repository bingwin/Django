/**
 * Created by chengwenhao on 2017/8/3.
 */

function openhref(url) {
    if (window.top !== window.self && /^https?:\/\//i.test(url)) try {
        window.top.location.href = url
    } catch (e) {
        location.href = url;
    } else location.href = url;
}
function openkwai(uri) {
    var device = {
        isIOS: function () {
            return !!navigator.userAgent.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/)
        },
        isAndroid: function () {
            return navigator.userAgent.indexOf("Android") > -1 || navigator.userAgent.indexOf("Adr") > -1
        },
        getIOSVersion: function () {
            if (!this.isIOS()) return !1;
            var n = navigator.userAgent.match(/OS (\d+)_(\d+)_?(\d+)?/);
            if (!n || n.length < 3) return !1;
            var i = parseFloat(parseInt(n[1], 10) + .1 * n[2]);
            return i > 0 && i
        },
        isInKwai: function () {
            return /Kwai\/|Kwai_Lite\/|Kwai_Pro\//i.test(navigator.userAgent) || n.getCookie("appver").length > 0
        },
        isInWeChat: function () {
            return /MicroMessenger/i.test(navigator.userAgent)
        },
        isInWeibo: function () {
            return /Weibo/i.test(navigator.userAgent)
        },
        isInQQ: function () {
            return / QQ\//i.test(navigator.userAgent)
        },
        isInQzone: function () {
            return /Qzone\//i.test(navigator.userAgent)
        },
        isInTBS: function () {
            return / TBS\//i.test(navigator.userAgent)
        },
        isInQQWebBrowser: function () {
            return /MQQBrowser/i.test(navigator.userAgent) && !this.isInWeChat() && !this.isInQQ() && !this.isInQzone() && !this.isInTBS()
        },
        isInBaidu: function () {
            return / baiduboxapp\//i.test(navigator.userAgent)
        },
        isInUC: function () {
            return / UCBrowser\//i.test(navigator.userAgent)
        },
        supportUniversalLink: function () {
            return this.getIOSVersion() >= 9
        },
        getBrowserDesc: function () {
            return this.isInQQ() ? "qq" : this.isInWeChat() ? "wechat" : this.isInQzone() ? "qzone" : this.isInWeibo() ? "weibo" : this.isInBaidu() ? "baidu" : this.isInUC() ? "uc" : this.isIOS() ? "ios" : this.isAndroid() ? "android" : ""
        },
        getDeviceHeightAndWidth: function () {
            var n = {
                dph: window && window.screen && window.screen.availHeight || 1,
                dpw: window && window.screen && window.screen.availWidth || 1
            };
            return void 0 !== window.devicePixelRatio && (n.dph *= window.devicePixelRatio, n.dpw *= window.devicePixelRatio),
                n
        }
    };

    if (device.isAndroid() || device.isIOS()) {
        //    移动端
        var url = "";
        if (device.isAndroid()) {
            if (device.isInWeChat()) {
                url = "http://a.app.qq.com/o/simple.jsp?pkgname=com.smile.gifmaker&g_f=99&android_scheme=" + encodeURIComponent("kwai://" + uri);
                openhref(url);
                return true
            } else {
                url = "kwai://" + uri;
            }
        } else if (device.isIOS()) {
            if (device.supportUniversalLink()) {
                url = "https://m.ssl.kuaishou.com/app/" + uri;
                openhref(url);
                return true;


            } else {
                url = "kwai://" + uri;
            }
        }
        var n = $("<iframe>");
        n.css("display", "none"), n.appendTo("body");
        n.attr("src", url);
        return true
    } else {
        //无法打开应用
        return false
    }


}

function openkwai_work(photoid) {
    return openkwai("work/" + photoid)
}
function openkwai_profile(photoid) {
    return openkwai("profile/" + photoid)
}



