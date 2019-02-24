/**
 * Created by Administrator on 2017/2/24.
 */
var hexcase = 0;
var b64pad = "";
var chrsz = 8;

function bbb(s) {
    return binl2hex(core_md5(str2binl(s), s.length * chrsz))
}
function b64_md5(s) {
    return binl2b64(core_md5(str2binl(s), s.length * chrsz))
}
function str_md5(s) {
    return binl2str(core_md5(str2binl(s), s.length * chrsz))
}
function hex_hmac_md5(a, b) {
    return binl2hex(core_hmac_md5(a, b))
}
function b64_hmac_md5(a, b) {
    return binl2b64(core_hmac_md5(a, b))
}
function str_hmac_md5(a, b) {
    return binl2str(core_hmac_md5(a, b))
}
function md5_vm_test() {
    return bbb("abc") == "900150983cd24fb0d6963f7d28e17f72"
}
function core_md5(x, e) {
    x[e >> 5] |= 0x80 << ((e) % 32);
    x[(((e + 64) >>> 9) << 4) + 14] = e;
    var a = 1732584193;
    var b = -271733879;
    var c = -1732584194;
    var d = 271733878;
    for (var i = 0; i < x.length; i += 16) {
        var f = a;
        var g = b;
        var h = c;
        var j = d;
        a = md5_ff(a, b, c, d, x[i + 0], 7, -680876936);
        d = md5_ff(d, a, b, c, x[i + 1], 12, -389564586);
        c = md5_ff(c, d, a, b, x[i + 2], 17, 606105819);
        b = md5_ff(b, c, d, a, x[i + 3], 22, -1044525330);
        a = md5_ff(a, b, c, d, x[i + 4], 7, -176418897);
        d = md5_ff(d, a, b, c, x[i + 5], 12, 1200080426);
        c = md5_ff(c, d, a, b, x[i + 6], 17, -1473231341);
        b = md5_ff(b, c, d, a, x[i + 7], 22, -45705983);
        a = md5_ff(a, b, c, d, x[i + 8], 7, 1770035416);
        d = md5_ff(d, a, b, c, x[i + 9], 12, -1958414417);
        c = md5_ff(c, d, a, b, x[i + 10], 17, -42063);
        b = md5_ff(b, c, d, a, x[i + 11], 22, -1990404162);
        a = md5_ff(a, b, c, d, x[i + 12], 7, 1804603682);
        d = md5_ff(d, a, b, c, x[i + 13], 12, -40341101);
        c = md5_ff(c, d, a, b, x[i + 14], 17, -1502002290);
        b = md5_ff(b, c, d, a, x[i + 15], 22, 1236535329);
        a = md5_gg(a, b, c, d, x[i + 1], 5, -165796510);
        d = md5_gg(d, a, b, c, x[i + 6], 9, -1069501632);
        c = md5_gg(c, d, a, b, x[i + 11], 14, 643717713);
        b = md5_gg(b, c, d, a, x[i + 0], 20, -373897302);
        a = md5_gg(a, b, c, d, x[i + 5], 5, -701558691);
        d = md5_gg(d, a, b, c, x[i + 10], 9, 38016083);
        c = md5_gg(c, d, a, b, x[i + 15], 14, -660478335);
        b = md5_gg(b, c, d, a, x[i + 4], 20, -405537848);
        a = md5_gg(a, b, c, d, x[i + 9], 5, 568446438);
        d = md5_gg(d, a, b, c, x[i + 14], 9, -1019803690);
        c = md5_gg(c, d, a, b, x[i + 3], 14, -187363961);
        b = md5_gg(b, c, d, a, x[i + 8], 20, 1163531501);
        a = md5_gg(a, b, c, d, x[i + 13], 5, -1444681467);
        d = md5_gg(d, a, b, c, x[i + 2], 9, -51403784);
        c = md5_gg(c, d, a, b, x[i + 7], 14, 1735328473);
        b = md5_gg(b, c, d, a, x[i + 12], 20, -1926607734);
        a = md5_hh(a, b, c, d, x[i + 5], 4, -378558);
        d = md5_hh(d, a, b, c, x[i + 8], 11, -2022574463);
        c = md5_hh(c, d, a, b, x[i + 11], 16, 1839030562);
        b = md5_hh(b, c, d, a, x[i + 14], 23, -35309556);
        a = md5_hh(a, b, c, d, x[i + 1], 4, -1530992060);
        d = md5_hh(d, a, b, c, x[i + 4], 11, 1272893353);
        c = md5_hh(c, d, a, b, x[i + 7], 16, -155497632);
        b = md5_hh(b, c, d, a, x[i + 10], 23, -1094730640);
        a = md5_hh(a, b, c, d, x[i + 13], 4, 681279174);
        d = md5_hh(d, a, b, c, x[i + 0], 11, -358537222);
        c = md5_hh(c, d, a, b, x[i + 3], 16, -722521979);
        b = md5_hh(b, c, d, a, x[i + 6], 23, 76029189);
        a = md5_hh(a, b, c, d, x[i + 9], 4, -640364487);
        d = md5_hh(d, a, b, c, x[i + 12], 11, -421815835);
        c = md5_hh(c, d, a, b, x[i + 15], 16, 530742520);
        b = md5_hh(b, c, d, a, x[i + 2], 23, -995338651);
        a = md5_ii(a, b, c, d, x[i + 0], 6, -198630844);
        d = md5_ii(d, a, b, c, x[i + 7], 10, 1126891415);
        c = md5_ii(c, d, a, b, x[i + 14], 15, -1416354905);
        b = md5_ii(b, c, d, a, x[i + 5], 21, -57434055);
        a = md5_ii(a, b, c, d, x[i + 12], 6, 1700485571);
        d = md5_ii(d, a, b, c, x[i + 3], 10, -1894986606);
        c = md5_ii(c, d, a, b, x[i + 10], 15, -1051523);
        b = md5_ii(b, c, d, a, x[i + 1], 21, -2054922799);
        a = md5_ii(a, b, c, d, x[i + 8], 6, 1873313359);
        d = md5_ii(d, a, b, c, x[i + 15], 10, -30611744);
        c = md5_ii(c, d, a, b, x[i + 6], 15, -1560198380);
        b = md5_ii(b, c, d, a, x[i + 13], 21, 1309151649);
        a = md5_ii(a, b, c, d, x[i + 4], 6, -145523070);
        d = md5_ii(d, a, b, c, x[i + 11], 10, -1120210379);
        c = md5_ii(c, d, a, b, x[i + 2], 15, 718787259);
        b = md5_ii(b, c, d, a, x[i + 9], 21, -343485551);
        a = safe_add(a, f);
        b = safe_add(b, g);
        c = safe_add(c, h);
        d = safe_add(d, j)
    }
    return Array(a, b, c, d)
}
function md5_cmn(q, a, b, x, s, t) {
    return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s), b)
}
function md5_ff(a, b, c, d, x, s, t) {
    return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t)
}
function md5_gg(a, b, c, d, x, s, t) {
    return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t)
}
function md5_hh(a, b, c, d, x, s, t) {
    return md5_cmn(b ^ c ^ d, a, b, x, s, t)
}
function md5_ii(a, b, c, d, x, s, t) {
    return md5_cmn(c ^ (b | (~d)), a, b, x, s, t)
}
function core_hmac_md5(a, b) {
    var c = str2binl(a);
    if (c.length > 16) c = core_md5(c, a.length * chrsz);
    var d = Array(16),
        opad = Array(16);
    for (var i = 0; i < 16; i++) {
        d[i] = c[i] ^ 0x36363636;
        opad[i] = c[i] ^ 0x5C5C5C5C
    }
    var e = core_md5(d.concat(str2binl(b)), 512 + b.length * chrsz);
    return core_md5(opad.concat(e), 512 + 128)
}
function safe_add(x, y) {
    var a = (x & 0xFFFF) + (y & 0xFFFF);
    var b = (x >> 16) + (y >> 16) + (a >> 16);
    return (b << 16) | (a & 0xFFFF)
}
function bit_rol(a, b) {
    return (a << b) | (a >>> (32 - b))
}
function str2binl(a) {
    var b = Array();
    var c = (1 << chrsz) - 1;
    for (var i = 0; i < a.length * chrsz; i += chrsz) b[i >> 5] |= (a.charCodeAt(i / chrsz) & c) << (i % 32);
    return b
}
function binl2str(a) {
    var b = "";
    var c = (1 << chrsz) - 1;
    for (var i = 0; i < a.length * 32; i += chrsz) b += String.fromCharCode((a[i >> 5] >>> (i % 32)) & c);
    return b
}
function binl2hex(a) {
    var b = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
    var c = "";
    for (var i = 0; i < a.length * 4; i++) {
        c += b.charAt((a[i >> 2] >> ((i % 4) * 8 + 4)) & 0xF) + b.charAt((a[i >> 2] >> ((i % 4) * 8)) & 0xF)
    }
    return c
}
function binl2b64(a) {
    var b = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var c = "";
    for (var i = 0; i < a.length * 4; i += 3) {
        var d = (((a[i >> 2] >> 8 * (i % 4)) & 0xFF) << 16) | (((a[i + 1 >> 2] >> 8 * ((i + 1) % 4)) & 0xFF) << 8) | ((a[i + 2 >> 2] >> 8 * ((i + 2) % 4)) & 0xFF);
        for (var j = 0; j < 4; j++) {
            if (i * 8 + j * 6 > a.length * 32) c += b64pad;
            else c += b.charAt((d >> 6 * (3 - j)) & 0x3F)
        }
    }
    return c
}
function i1(b) {
    b = decodeURI(b);
    var a;
    a = b.split("&");
    a.sort();
    b = a.join("");
    return bbb(b + '382700b563f4')
}
function il(c) {
    var a = document.createElement('a');
    a.href = c;
    return {
        source: c,
        protocol: a.protocol.replace(':', ''),
        host: a.hostname,
        port: a.port,
        query: a.search,
        params: (function () {
            var b = {},
                seg = a.search.replace(/^\?/, '').split('&'),
                len = seg.length,
                i = 0,
                s;
            for (; i < len; i++) {
                if (!seg[i]) {
                    continue
                }
                s = seg[i].split('=');
                b[s[0]] = s[1]
            }
            return b
        })(),
        file: (a.pathname.match(/\/([^\/?#]+)$/i) || [, ''])[1],
        hash: a.hash.replace('#', ''),
        path: a.pathname.replace(/^([^\/])/, '/$1'),
        relative: (a.href.match(/tps?:\/\/[^\/]+(.+)/) || [, ''])[1],
        segments: a.pathname.replace(/^\//, '').split('/')
    }
}
function ad(l, i) {
    return Math.floor(Math.random() * (i - l + 1) + l)
}
function ll(a) {
    var q = "";

    var b = "0123456789abcdef";
    var c = b.length - 1;
    for (var i = 0; i < a; i++) {
        q += b[ad(0, c)]
    }
    return q
}
function ii() {
    var f = 'ANDROID_' + ll(16);

    var userid = Math.random() * (3999999999 - 1) + 1;
    userid = parseInt(userid, 10);
    var token = bbb(userid) + "-" + userid;

    var url = "http://api.ksapisrv.com/rest/n/clc/click";
    var urlparam = "lat=NaN&lon=NaN&ver=4.53&ud=0&sys=ANDROID_4.4.2&c=BAIDU&oc=BAIDU&net=WIFI&did=" + f + "&mod=OPPO%28R7Plus%29&app=0&language=zh-cn&country_code=CN&appver=4.53.3.3098";
    var postparam = "client_key=3c2cd3f3&token=" + token + "&os=android&data=" + photo + "_p7&downs=";
    url = url + "?" + urlparam;
    postparam = postparam + "&sig=" + i1(postparam + "&" + urlparam);
    var o = new Object();
    o.url = url;
    o.post = postparam;
    return o
}


$(document).ready(function () {
    var i = 0;
    var s = 0;
    var e = 0;
    var f = 0;
    photo = null;
    $(document).on("click", ".selectphoto", function () {
        photo = $(this).attr("data-photo");
        $.closePopup()
    });

    $('#start').click(function () {
        var c = $("#num").val();
        var d = $("#yanchi").val();
        if (!photo) {
            alert("没选择作品");
        } else if (!c) {
            alert("你还没有输入要刷的阅读量")
        } else {
            if (i < c) {
                $('#wait').html("正在刷快手阅读量中.....");
                var o = ii();
                $.ajax({
                    type: "POST",
                    url: o.url,
                    data: o.post,
                    success: function (a) {
                        s++;
                        $('#wait').html("已执行" + i + "次，已刷" + s + "个阅读量，" + d + "秒后继续刷~~~")
                    },
                    error: function (a) {
                        s++;
                        $('#wait').html("已执行" + i + "次，已刷" + s + "个阅读量，" + d + "秒后继续刷~~~")
                    }
                });
                setTimeout(function () {
                    $('#start').click()
                }, d * 1000);
                ++i;
                $('#wait').html("已执行" + i + "次，已刷" + s + "个阅读量，" + d + "秒后继续刷~~~")
            } else {
                if (i == s) {
                    $('#wait').html("执行完毕！共执行" + i + "次，刷了" + s + "个阅读量");
                    e = 0;
                    f = 0;
                    s = 0;
                    i = 0
                }
            }
        }
    })
});