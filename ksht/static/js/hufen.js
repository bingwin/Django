//json语法的js

var hufen = {
    ajaxflow: function (flowid, status) {
        $.ajax({
            url: "/hufen/flow",
            type: 'POST',
            data: {"flowid": flowid, "status": status},
            async: false,
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                resultdata = data;
            }
        });
        return resultdata;
    },

    flow: function (flowobj) {
        console.log(flowobj);
        if (flowobj.type == 1) {
            switch (flowobj.flowstatus) {
                case 0:
                    hufen.confirm(flowobj.flowid, flowobj.user);
                    break;
                case -1:
                    $.alert("有一方拒绝互粉,结束本次互粉");
                    break;
                case 1:
                    hufen.follow(flowobj.flowid, flowobj.user, 2);
                    break;
                case -2:
                    console.log("您关注B失败，扣信誉值1点");
                    break;
                case 2:
                    console.log("关注成功，等待B确认");
                    break;
                case -3:
                    console.log("对方认为您没有关注他，请取消关注对方，结束本次互粉");
                    break;
                case 3:
                    console.log("对方已确认，等待对方关注您");
                    break;
                case -4:
                    console.log("对方关注您失败，请取关对方，结束本次互粉");
                    break;
                case 4:
                    console.log("等待您确认对方是否关注您");
                    break;
                case -5:
                    console.log("您认为对方没有关注您，请取消关注对方");
                    break;
                case 5:
                    console.log("互粉完成。是否开始下一次互粉");
                    break;
            }
        } else {
            switch (flowobj.flowstatus) {
                case 0:
                    hufen.confirm(flowobj.flowid, flowobj.user);
                    break;
                case -1:
                    $.alert("有一方拒绝互粉");
                    break;
                case 1:
                    console.log("等待对方关注您");
                    break;
                case -2:
                    console.log("对方关注您失败，是否重新开始互粉");
                    break;
                case 2:
                    console.log("请您确认对方已经关注您");
                    break;
                case -3:
                    console.log("您认为对方没有关注您，结束互粉");
                    break;
                case 3:
                    console.log("请关注对方");
                    break;
                case -4:
                    console.log("关注失败，结束互粉");
                    break;
                case 4:
                    console.log("等待对方确认");
                    break;
                case -5:
                    console.log("对方认为您没有关注他，请取关对方");
                    break;
                case 5:
                    console.log("互粉成功");
                    break;
            }
        }
    },

    getksinfo: function (ksid) {
        $.ajax({
            url: "http://101.200.153.182:8000/rest/n/feed/profile?count=0&pcursor=&user_id=" + ksid,
            async: false,
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                userdata = data;
            }
        });
        return userdata
    },

    confirmts: function (user) {
        var userdata = hufen.getksinfo(user.ksid);

        var temp = '<img src="' + userdata.owner_head + '" height="86xp" width="86xp" style="border-radius:50%">' +
            '<div id="user-name">' + userdata.owner_name + '</div>' +
            '<div class="user-id" >快手ID：' + user.ksid + '</div>' +
            '<div class="user-num">' +
            '<a class="user-num-item first dbl">' +
            '<span class="user-txt">' + userdata.owner_count.fan + '</span>' +
            '<span class="user-txt-1">粉丝</span>' +
            '</a>' +
            '<a class="user-num-item dbl">' +
            '<span class="user-txt">' + userdata.owner_count.follow + '</span>' +
            '<span class="user-txt-1">关注</span>' +
            '</a>' +
            '<a class="user-num-item dbl">' +
            '<span class="user-txt">' + userdata.owner_count.photo + '</span>' +
            '<span class="user-txt-1">作品</span>' +
            '</a>' +
            "</div>" +
            '<div class="user-num">' +
            '<a class="user-num-item first dbl">' +
            '<span class="user-txt">' + user.credit + '</span>' +
            '<span class="user-txt-1">信誉值</span>' +
            '</a>' +
            "</div>";

        $.modal({
            title: "确认互粉",
            text: temp,
            buttons: [
                {
                    text: "与他互粉", onClick: function () {
                    hufen.confirm(user, 1)
                }
                },
                {
                    text: "换一个人", className: "default", onClick: function () {
                    hufen.confirm(user, -1);
                }
                },
            ]
        });
    },

    confirmwait: function () {

    },

    confirm: function (user, status) {
        $.showLoading("数据提交中");
        $.post("/hufen/pairconfirm", {"userid": user.userid, "status": status}, function (data) {
            $.hideLoading();
            console.log(data);
            if (data.err == 0) {
                hufen.confirmwait(user);
            } else if (data.err == 1) {
                $.alert("匹配用户成功，点击确定后刷新页面，然后去列表关注对方", "提示", function () {
                    window.location.href = "/hufen"
                })
            }
            else {
                $.alert(data.msg);
            }
        }, "json").error(function () {
            // setTimeout(hufen.pair, 1000);
        });
    },


    follow: function (flowid, user, status) {
        var userdata = hufen.getksinfo(user.userid);
        var temp = '<img src="' + userdata.owner_head + '" height="86xp" width="86xp" style="border-radius:50%">' +
            '<div id="user-name">' + userdata.owner_name + '</div>' +
            '<div class="user-id" >快手ID：' + user.userid + '</div>' +
            '<div>请在同意互粉后1分钟内关注对方</div>';
        $.modal({
            title: "关注对方",
            text: temp,
            buttons: [
                {
                    text: "去关注", onClick: function () {
                    window.location.href = "kwai://profile/" + user.userid;
                    $.modal({
                        title: "关注对方",
                        text: temp + "<div>如果没有跳转到对方首页，请手动关注</div>",
                        buttons: [
                            {
                                text: "已关注", onClick: function () {
                                hufen.ajaxflow(flowid, status)
                            }
                            }, {
                                text: "无法关注", className: "default", onClick: function () {
                                    hufen.ajaxflow(flowid, -status)
                                }
                            }
                        ]
                    });
                }
                }
            ]
        });
    },

    pair: function () {
        $.hideLoading();
        $.showLoading("正在匹配");
        $.post("/hufen/pair", {}, function (data) {
            console.log(data);
            if (data.err == 0) {
                $.hideLoading();
                hufen.confirmts(data.user);
            } else {
                setTimeout(hufen.pair, 5000);
            }
        }, "json").error(function () {
            setTimeout(hufen.pair, 1000);
        });
    }


};


showmsg = "正在配对";

function show() {
    alert("Hello World!");
}

function start(flowid, status) {
    $.ajax({
        url: "/hufen/flow",
        type: 'POST',
        data: {"flowid": flowid, "status": status},
        async: false,
        dataType: "json",
        success: function (data, textStatus, jqXHR) {
            resultdata = data;
        },

    });
    return resultdata;

}

function confirm(flowid, user) {
    $.ajax({
        url: "http://101.200.153.182:8000/rest/n/feed/profile?count=0&pcursor=&user_id=" + user.userid,
        async: false,
        dataType: "json",
        success: function (data, textStatus, jqXHR) {
            userdata = data;
            console.log(userdata);
        }
    });
    var temp = '<img src="' + userdata.owner_head + '" height="86xp" width="86xp" style="border-radius:50%">' +
        '<div id="user-name">' + userdata.owner_name + '</div>' +
        '<div class="user-id" >快手ID：' + user.userid + '</div>' +
        '<div class="user-num">' +
        '<a class="user-num-item first dbl">' +
        '<span class="user-txt">' + userdata.owner_count.fan + '</span>' +
        '<span class="user-txt-1">粉丝</span>' +
        '</a>' +
        '<a class="user-num-item dbl">' +
        '<span class="user-txt">' + userdata.owner_count.follow + '</span>' +
        '<span class="user-txt-1">关注</span>' +
        '</a>' +
        '<a class="user-num-item dbl">' +
        '<span class="user-txt">' + userdata.owner_count.photo + '</span>' +
        '<span class="user-txt-1">作品</span>' +
        '</a>' +
        "</div>" +
        '<div class="user-num">' +
        '<a class="user-num-item first dbl">' +
        '<span class="user-txt">' + user.credit + '</span>' +
        '<span class="user-txt-1">信誉值</span>' +
        '</a>' +
        "</div>";

    $.modal({
        title: "确认互粉",
        text: temp,
        buttons: [
            {
                text: "与他互粉", onClick: function () {
                start(flowid, 1);
            }
            },
            {
                text: "换一个人", className: "default", onClick: function () {
                start(flowid, -1);
            }
            },
        ]
    });
}

// $(function () {
//
//     $("#hufen_start").click(function () {
//         $.showLoading(showmsg);
//         $.post("/hufen/pair", {}, function (data) {
//                 $.hideLoading();
//                 console.log(data);
//                 if (data.err == 0) {
//
//                     var flowstatus = data["flow"]["flowstatus"];
//                     var self = data["flow"]["self"];
//                     var user = data["flow"]["user"];
//
//                     switch (flowstatus) {
//                         case 0:
//                             if (self["flowstatus"] == 2) {
//                                 showmsg = "等待对方同意互粉";
//                             } else {
//                                 confirm(data["flow"]["flowid"], user);
//                             }
//                             ;
//                             break;
//                         default:
//                             $("#hufen_start").click();
//                     }
//                 }
//
//
//             }, "json"
//         ).error(function () {
//             $.hideLoading();
//         });
//     });
//
// });
function keepalive( ws ){
    if (ws.bufferedAmount == 0){
        ws.send(JSON.stringify({"action":"heartbeat"}));
    }

}


$(function () {
    var ws;
        function onLoad() {
        ws = new WebSocket("ws://"+window.location.host+"/ws");

        ws.onopen = function (evt) {
            heartbeat_timer = setInterval( function(){keepalive(ws)}, 10000 );
        };      // 建立连接
        ws.onmessage = function (evt) {    // 获取服务器返回的信息
            console.log(evt.data);
            data = $.parseJSON(evt.data);
            if (data['from'] == 'sys') {

            }
        };
        ws.onerror = function (evt) {
        }
    }

    onLoad();

    $("#hufen_start").click(function () {
        ws.send(JSON.stringify({"action":"pair"}))

    });


});
