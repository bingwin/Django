
var time = 60; //统一设置加载时延 单位:秒
var overtime = 10; //统一设置不同操作的时间间隔上限
var statime;  //开始时间
var endtime;  //结束时间
var difftime; //相差时间 秒
var temp; //提示信息
var check = 0; //计时开关
var ws = new WebSocket("ws://"+window.location.host+"/history");
ws.onopen = function (evt) {
    console.log("open!")
};// 建立连接
ws.onmessage = function (evt) {    // 获取服务器返回的信息
    layer.closeAll();
    check = 0;
    console.log(evt.data);
    data = JSON.parse(evt.data);
    if ('action' in data) {
        switch (data.action) {
            case 'check':
                layer.closeAll();
                openkwai_profile(data.userid);
                break;
        };
        temp = '<span class="user-txt-1">是否返回互粉大厅？</span>';
        layer.open({
            content: temp,
            btn: ['返回大厅','留在本页'],
            yes: function () {
                history.back(-1);
                return false
            },
            btn2:function (index) {
                layer.close(index);
            },
            cancel: function () {

            }
        });
    };
};
ws.onclose = function () {
    console.log("close!")
}
ws.onerror = function (evt) {
    console.log("error!")
}

$(document).ready(function(){
    $("#CheckFocus").click(function () {
        ws.send(JSON.stringify({"action": "CheckSelf"}));
    });
    $("#CheckFollow").click(function () {
        ws.send(JSON.stringify({"action": "CheckSelf"}));
    });
    $("#RetToHall").click(function () {
        history.back(-1);
    });
});

layer.config({
type:0,
title: '提示',
anim: 5,
btnAlign: 'c',
closeBtn: 1,
shade: 0.5,
shadeClose:false,
skin: 'layui-layer-molv'});

function onloading(text) {
    var msg = layer.msg(text,{
        icon: 6,
        time: time*1000,
    });//等待time秒
    statime = new Date();
}

function CheckTime() {
    if(check) {
        endtime = new Date();
        difftime = (endtime.getTime() - statime.getTime()) / 1000;
        console.log(difftime);
        if (difftime >= overtime) { //等待服务器响应超过60s
            check = 0;
            ws.send(JSON.stringify({"action": "OverTime"}));
            temp = '<div>等待服务器响应超时，互粉结束</div>';
            layer.open({
                content: temp,
                btn: ['重新匹配', '冷静一下'],
                yes: function () {
                    layer.closeAll();
                    ws.send(JSON.stringify({
                        "action": "repair",
                        "state": "secondrepair"
                    }));//后提出换人
                    temp = '<div>正在重新匹配，请稍等...</div>';
                    onloading(temp);
                    check = 0;
                    return false
                },
                btn2: function (index) {
                    layer.close(index);
                },
                cancel: function () {
                    //						      右上角关闭回调
                }
            });
        };
    };
}

//取关对方 举报对方取关
function CancelFocus(handler,uid,flag) {
    if(flag == 1){ //主动取消关注，警告提示
        temp = '<span class="user-txt-1">举报对方取关并去取关对方，是否确认？（请勿恶意举报哦亲~）</span>';
    }
    else{
        temp = '<span class="user-txt-1">是否确认取消关注？</span>';
    }
    layer.open({
        content: temp,
        btn: ['继续取关','调戏一下'],
        yes: function () {
            // 关闭按钮 重加载后会恢复
            $(handler).attr("disabled", true);
            $(handler).attr("class", "btn weui_btn weui_btn_mini weui_btn_disabled weui_btn_default");
            openkwai_profile(uid);
            layer.closeAll();
            ws.send(JSON.stringify({
                "action": "CancelFocus",
                "otherid":uid}));
            return false
        },
        btn2:function (index) {
            layer.close(index);
        },
        cancel: function (index) {

        }
    });
}

function ReFocus(handler,uid,flag) {
    layer.alert("NoWork!");
}

setInterval(CheckTime,2000); //每两秒检查一次是否超时
