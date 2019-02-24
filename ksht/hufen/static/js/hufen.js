
var time = 65; //统一设置加载时延 单位：秒
var overtime = 60; //统一设置不同操作的时间间隔上限 单位：秒
var overstate; //0-互粉中超时 1-匹配中超时(用户量大，匹配慢)
var statime;  //开始时间
var endtime;  //结束时间
var difftime; //相差时间 秒
var temp; //提示信息
var check = 0; //计时开关

var ws;//websocket实例
var lockReconnect = false;//避免重复连接
var wsUrl = "ws://"+window.location.host+"/hufen";
createWebSocket(wsUrl);
//var ws = new WebSocket("ws://"+window.location.host+"/hufen");

function createWebSocket(url) {
    try {
        ws = new WebSocket(url);
        initEventHandle();
    } catch (e) {
        reconnect(url);
    }
}

function initEventHandle() {
    ws.onopen = function (evt) {
        //心跳检测重置
        heartCheck.reset().start();
        console.log("open!")
    };// 建立连接
    ws.onmessage = function (evt) {    // 获取服务器返回的信息
        layer.closeAll();
        rebtn(); //打开按钮
        check = 0;
        //        console.log(evt.data);
        data = JSON.parse(evt.data);
        if ('action' in data) {
            switch (data.action) {
                case 'pair':
                    temp =
                        '<div class="user-name">用户名：' + data.username + '</div>' +
                        '<div class="user-id" >快手ID：' + data.userid + '</div>' +
                        '<div class="user-txt-1" >作品数：' + data.photo + '</div>' +
                        '<div class="user-txt-1" >信誉值：' + data.credit + '</div>' +
                        '<div class="user-txt-1" >总互粉次数：' + data.totletime + '</div>' +
                        '<div class="user-txt-1" >互粉成功率：' + (100 * (data.sucrate)).toFixed(2) + ' %</div>';
                    layer.open({
                        content: temp,
                        btn: ['确认互粉', '换个老铁'],
                        yes: function () {
                            //						      确认的回调
                            ws.send(JSON.stringify({"action": "dopair"}));
                            temp = '<div>正在等待对方确认，请稍等...</div>';
                            onloading(temp);
                            check = 1;
                            overstate = 0;
                            return false
                        },
                        btn2: function () {
                            //						      	换个老铁的回调
                            layer.closeAll();
                            ws.send(JSON.stringify({"action": "change"}));//换人
                            temp = '<div>正在重新匹配，请稍等...</div>';
                            onloading(temp);
                            check = 1;
                            overstate = 1;
                            return false //禁止点击该按钮关闭
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('是否确认取消此次互粉')) {
                                ws.send(JSON.stringify({"action": "CancelPairSecond"}));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//双方确认是否进行互粉
                case 'dopairfirst': //确认要互粉了，低信誉值用户先关注
                    temp =
                        '<div class="user-id" >快手ID：' + data.userid +
                        '<span class="user-txt-1">愿意与您互粉</span></div>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['去关注TA', '不关注TA'],
                        yes: function () {
                            //						      	确认的回调
                            openkwai_profile(data.userid);
                            layer.closeAll();
                            ws.send(JSON.stringify({"action": "ConfirmPairFirst"}));
                            return false
                        },
                        btn2: function (index) {
                            if (confirm('此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmPairFirst",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            if (confirm('此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmPairFirst",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break; //低信誉值用户选择是否去快手关注匹配用户
                case 'dopairsecond':
                    switch (data.state) {
                        case 'wait':
                            temp = '<div>对方正在关注您，请稍等...</div>';
                            break;
                        case 'makeconfirm':
                            temp = '<div>对方正在确认您是否已经关注TA，请稍等...</div>';
                            break;
                    };
                    onloading(temp); //等待对方关注您
                    check = 1;
                    overstate = 0;
                    break;//高信誉值用户等待对方确认与关注
                case 'dofocusfirst':
                    switch (data.state) {
                        case 'makeconfirm':
                            temp = '<div>对方正在确认您是否已经关注TA，请稍等...</div>';
                            break;
                        case 'makefocus':
                            temp = '<div>对方已确认您关注了TA，请稍等...</div>';
                            break;
                        case 'dofocus':
                            temp = '<div>对方正在关注您，请稍等...</div>';
                            break;
                    };
                    onloading(temp);
                    check = 1;
                    overstate = 0;
                    break;//低信誉值用户等待对方确认与关注
                case 'dofocussecond':
                    temp = '<span class="user-txt-1">是否已经关注对方</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['已经关注', '没有关注'],
                        yes: function () {
                            //						      	确认的回调
                            ws.send(JSON.stringify({"action": "ConfirmSuccessFirst"}));
                            layer.closeAll();
                            temp = '<div>对方正在关注您，请稍等...</div>';
                            onloading(temp);
                            check = 1;
                            overstate = 0;
                            return false
                        },
                        btn2: function (index) {
                            if (confirm('您已确认对方关注了你，若此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmSuccessFirst",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            //						      	右上角关闭回调
                            if (confirm('您已确认对方关注了你，若此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmSuccessFirst",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//高信誉值用户选择是否已经关注对方
                case 'doconfirmfirst':
                    temp = '<span class="user-txt-1">是否已经关注对方</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['已经关注', '没有关注'],
                        yes: function () {
                            //						      	确认的回调
                            ws.send(JSON.stringify({"action": "ConfirmFocusFirst"}));
                            layer.closeAll();
                            temp = '<div>对方正在关注您，请稍等...</div>';
                            onloading(temp);
                            check = 1;
                            overstate = 0;
                            return false
                        },
                        btn2: function (index) {
                            if (confirm('此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusFirst",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            //						         右上角关闭回调
                            if (confirm('此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusFirst",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//低信誉值用户选择是否已经关注匹配用户
                case 'doconfirmpre':
                    temp = '<span class="user-txt-1">对方是否已经关注您</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['已经关注', '没有关注'],
                        yes: function () {
                            //						      	确认的回调
                            ws.send(JSON.stringify({"action": "ConfirmFocusPre"}));
                            layer.closeAll();
                            return false
                        },
                        btn2: function (index) {
                            if (confirm('如果确认对方没有关注则互粉结束，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusPre",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('请选择对方是否已经关注您，否则互粉结束，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusPre",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//高信誉值用户选择对方是否已经关注自己
                case 'doconfirmsecond'://高信誉值用户选择是否
                    temp = '<span class="user-txt-1">是否愿意关注对方</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['去关注TA', '不关注TA'],
                        yes: function () {
                            //						      	确认的回调
                            openkwai_profile(data.userid);
                            layer.closeAll();
                            ws.send(JSON.stringify({"action": "ConfirmFocusSecond"}));
                            return false
                        },
                        btn2: function (index) {
                            //						      	取消的回调
                            if (confirm('您已确认对方关注了您，若此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusSecond",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('您已确认对方关注了您，若此时取消关注则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmFocusSecond",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//高信誉值用户选择是否去快手关注对方
                case 'checkfocusfirst':
                    temp = '<span class="user-txt-1">对方已关注您，请去粉丝列表确认</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['去快手粉丝列表确认'],
                        yes: function () {
                            openkwai_profile(data.userid);
                            layer.closeAll();
                            ws.send(JSON.stringify({"action": "CheckFocusFirst"}));
                            return false
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('此时取消确认则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoCheckFocusFirst"}));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//高信誉值用户选择是否去快手确认对方是否关注
                case 'checkfocussecond':
                    temp = '<span class="user-txt-1">对方已关注您，请去粉丝列表确认</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['去快手粉丝列表确认'],
                        yes: function () {
                            //						      	确认的回调
                            openkwai_profile(data.userid);
                            layer.closeAll();
                            ws.send(JSON.stringify({"action": "CheckFocusSecond"}));
                            return false
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('此时取消确认则互粉失败，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoCheckFocusSecond"}));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//低信誉值用户选择是否去快手确认对方是否关注
                case 'doconfirmfin':
                    temp = '<span class="user-txt-1">对方是否已经关注您</span>' +
                        '<div align="center" class="user-txt-1"><span>请在' + overtime.toString() + '秒内操作</span></div>';
                    layer.open({
                        content: temp,
                        btn: ['已经关注', '没有关注'],
                        yes: function () {
                            //						      	确认的回调
                            ws.send(JSON.stringify({"action": "ConfirmSuccessSecond"}));
                            layer.closeAll();
                            return false
                        },
                        btn2: function (index) {
                            if (confirm('如果确认对方没有关注则互粉结束，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmSuccessSecond",
                                    "state": "deny"
                                }));
                                layer.close(index);
                            }
                            return false
                        },
                        cancel: function (index) {
                            //						        右上角关闭回调
                            if (confirm('请确认对方是否已经关注您，否则互粉结束，是否确认！')) {
                                ws.send(JSON.stringify({
                                    "action": "NoConfirmSuccessSecond",
                                    "state": "cancel"
                                }));
                                layer.close(index);
                            }
                            return false
                        }
                    });
                    break;//低信誉值用户选择对方是否已经关注自己
                case 'dopairsuccess':
                    // 更新积分
                    $("#integral").text(data.integral);
                    temp =
                        '<div class="user-id" >恭喜与' + data.userid +
                        '<span class="user-txt-1">互粉成功</span>' +
                        '<span class="user-txt-1">扣除积分:' + data.cost + '</span></div>';
                    layer.open({
                        title: '互粉结束',
                        content: temp,
                        btn: ['确认'],
                        yes: function () {
                            //						      	确认的回调
                            layer.closeAll();
                            return false
                        },
                        cancel: function () {
                            //						      右上角关闭回调
                        }
                    });
                    break;//双方匹配成功
                //正确与异常分割线
                case 'errorpair':
                    switch (data.state) {
                        case 'change':
                            temp = '<div>对方选择了换一个人，互粉结束</div>';
                            dorepair();
                            break;
                        case 'cancelpair':
                            temp = '<div>对方取消了本次互粉，互粉结束</div>';
                            dorepair();
                            break;
                        case 'ErrorDU_0':
                            temp = '<div>对方取消了去确认您是否关注，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorDU_1_1':
                            temp = '<div>对方取消去关注您，互粉结束</div>';
                            dorepair();
                            break;

                        case 'ErrorDU_1_2':
                            temp = '<div>对方拒绝去关注您，互粉结束</div>';
                            dorepair();
                            break;

                        case 'ErrorDU_2_1':
                            temp = '<div>对方取消确认是否已经关注您，互粉结束</div>';
                            dorepair();
                            break;

                        case 'ErrorDU_2_2':
                            temp = '<div>对方选择没有关注您，互粉结束</div>';
                            dorepair();
                            break;

                        case 'ErrorDU_3_1':
                            temp = '<div>对方确认之后没有选择您是否关注了TA，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_1_1':
                            temp = '<div>对方确认之后没有选择您是否关注了TA，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorDU_3_2':
                            temp = '<div>对方确认之后反映您没有关注TA，互粉结束，若您已关注对方请取关</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_1_2':
                            temp = '<div>对方确认之后反映您没有关注TA，互粉结束，若您已关注对方请取关</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_0':
                            temp = '<div>对方取消了去确认您是否关注，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_2_1':
                            temp = '<div>对方取消去关注您，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_2_2':
                            temp = '<div>对方拒绝去关注您，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_3_1':
                            temp = '<div>对方取消确认是否已经关注您，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'ErrorGU_3_2':
                            temp = '<div>对方选择没有关注您，互粉结束，请取关对方</div>';
                            docelfocus(data.otherid);
                            break;

                        case 'workovertime':
                            temp = '<div>互粉操作超时，互粉结束</div>';
                            check = 0;
                            dorepair();
                            break;
                        case 'waitovertime':
                            temp = '<div>等待服务器响应超时，互粉结束</div>';
                            check = 0;
                            dorepair();
                            break;
                    };
                    break;//有一方在确认互粉之初取消了
            };
        }
        if ('error' in data) {
            switch (data.error) {
                case 'nopair':
                    temp = '<div>没有找到合适用户，匹配结束</div>';
                    dorepair();
                    break;
                case 'server':
                    temp = '<div>服务器异常，本次互粉结束</div>';
                    dorepair();
                    break;
            };
        };
        //如果获取到消息，心跳检测重置
        //拿到任何消息都说明当前连接是正常的
        heartCheck.reset().start();
    }

    ws.onclose = function () {
        console.log("close!")
        reconnect(wsUrl);
    }

    ws.onerror = function (evt) {
        console.log("error!")
        reconnect(wsUrl);
    }
}

function reconnect(url) {
    if(lockReconnect) return;
    lockReconnect = true;
    //没连接上会一直重连，设置延迟避免请求过多
    setTimeout(function () {
        createWebSocket(url);
        lockReconnect = false;
    }, 2000);
}

var heartCheck = {
    timeout: 60000,//60秒
    timeoutObj: null,
    serverTimeoutObj: null,
    reset: function(){
        clearTimeout(this.timeoutObj);
        clearTimeout(this.serverTimeoutObj);
        return this;
    },
    start: function(){
        var self = this;
        this.timeoutObj = setTimeout(function(){
            //这里发送一个心跳，后端收到后，返回一个心跳消息，
            //onmessage拿到返回的心跳就说明连接正常
            ws.send("HeartBeat");
            self.serverTimeoutObj = setTimeout(function(){//如果超过一定时间还没重置，说明后端主动断开了
                ws.close();//如果onclose会执行reconnect，我们执行ws.close()就行了.如果直接执行reconnect 会触发onclose导致重连两次
            }, self.timeout)
        }, this.timeout)
    }
}


$(document).ready(function(){
    $("#hufen_start").click(function () {
        ws.send(JSON.stringify({"action":"pair"}));
//        	$("body").showLoading();
        temp = '<div>正在匹配合适用户，请稍等...</div>';
        onloading(temp);
        check = 1;
        overstate = 1;
    });
    $("#hufen_history").click(function () {
//        	window.open('list');//新建窗口打开互粉列表
        window.location.href = 'list';//原窗口创建
    });
    $("#delete_record").click(function () {
        ws.send(JSON.stringify({"test":"delete"}));
    });
})

layer.config({
type:0,
title: '互粉进行中',
anim: 5,
btnAlign: 'c',
closeBtn: 1,
shade: 0.5,
shadeClose:false,
skin: 'layui-layer-molv'})

function onloading(text) {
    var msg = layer.msg(text,{
        icon: 6,
        time: time*1000,
    });//等待time秒
    disbtn(); //加载时关闭按钮
    statime = new Date();
}

// 超时前提
function CheckTime() {
    if(check) {
        endtime = new Date();
        difftime = (endtime.getTime() - statime.getTime()) / 1000;
        console.log(difftime);
        if (difftime >= overtime) { //等待服务器响应超过60s
            check = 0;
            // 互粉中超时
            if (overstate == 0){
                ws.send(JSON.stringify({"action": "OverTime","state":"InHufen"}));
            }
            // 匹配中超时
            else{
                ws.send(JSON.stringify({"action": "OverTime","state":"InPair"}));
            }
            temp = '<div>等待服务器响应超时，互粉结束</div>';
            dorepair();
        };
    };
}

function dorepair() {
    layer.open({
        content: temp,
        btn: ['重新匹配', '冷静一下'],
        yes: function () {
            //						      	确认的回调
            layer.closeAll();
            ws.send(JSON.stringify({"action": "repair"}));//后提出换人
            temp = '<div>正在重新匹配，请稍等...</div>';
            onloading(temp);
            check = 1;
            overstate = 1;
            return false
        },
        btn2: function (index) {
            rebtn();
            layer.close(index);
        },
        cancel: function () {
            rebtn();
            //						      右上角关闭回调
        }
    });
}

// 提示取消关注
function docelfocus(otherid) {
    layer.open({
        content: temp,
        btn: ['去取消关注'],
        yes: function () {
            //						      	确认的回调
            layer.closeAll();
            openkwai_profile(otherid);
            temp = '<div>现在开始匹配？</div>';
            dorepair();
            return false
        },
        cancel: function (index) {
            if (confirm('若您未取关对方则会消耗今日的关注次数，是否确认退出！')) {
                layer.close(index);
                temp = '<div>现在开始匹配？</div>';
                dorepair();
            };
            return false
        }
    });
}

function disbtn() {
    $("#hufen_start").attr("disabled", true);
    $("#hufen_history").attr("disabled", true);
    $("#delete_record").attr("disabled", true);
    $("#hufen_start").attr("class", "weui_btn weui_btn_disabled weui_btn_default");
    $("#hufen_history").attr("class", "weui_btn weui_btn_disabled weui_btn_default");
    $("#delete_record").attr("class", "weui_btn weui_btn_disabled weui_btn_default");
}

function rebtn() {
    $("#hufen_start").attr("disabled", false);
    $("#hufen_history").attr("disabled", false);
    $("#delete_record").attr("disabled", false);
    $("#hufen_start").attr("class", "weui_btn weui_btn_primary");
    $("#hufen_history").attr("class", "weui_btn weui_btn_primary");
    $("#delete_record").attr("class", "weui_btn weui_btn_warn");
}

setInterval(CheckTime,1000) //每1秒检查一次是否超时
