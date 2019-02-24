/**
 * Created by chengwenhao on 2017/6/12.
 */
$.ajaxSetup({
    async: false
});
$(function () {
    $("#btn_setuserid").click(function () {
        $.prompt("请输入快手ID", "提示", function (input) {
            input = parseInt(input, 10);
            if (!isNaN(input)) {
                userid = input;
                window.location.href = "/live/rq?userid="+userid;
            } else {
                $.alert("请输入用户ID", "提示", function () {
                    $("#btn_setuserid").click();
                })
            }
        }, function () {

        }, userid);
    });

    // $("#btn_start").click(function () {
    //     if (liveStreamId == null){
    //         $.alert("请先开启直播")
    //     }
    //
    //
    //     if (datas.length > 0 && sids.length == 0) {
    //         for (var i = 0; i < 50; i++) {
    //             rq(datas[i])
    //         }
    //     }
    // })

});

var datas = [];
var socketManager = null;

var sids = new Array();



function getuserinfo() {

    getliveStreamId(userid, function (state, streamid) {
        if (streamid == null) {
            $("#state").text("未开始直播");
        } else {
            if (liveStreamId == null || liveStreamId != streamid) {
                if (liveStreamId != streamid){
                    btninit();
                }

                liveStreamId = streamid;

                $.post("/live/getdata", {"streamid": liveStreamId}, function (data, textStatus, jqXHR) {
                    datas = data["datas"]

                }, "json");
            }

            live_users(streamid, function (ret, err) {
                $("#state").text(ret["watchingCount"]);


                // if (datas.length > 0 && sids.length == 0) {
                //     for (var i = 0; i < 50; i++) {
                //         rq(datas[i])
                //     }
                // }


            });


        }
    })


    // setInterval(getuserinfo,1000);


}
function heartbeat(sid) {

    if (sids.indexOf(sid) == -1) {
        return
    } else {
        socketManager.write({
            sid: sid,
            data: 'ARorPAAAAAAAAAAAAAAACAgBEAEaAggA',
            base64: true
        }, function (ret, err) {
//                alert(JSON.stringify(ret));
        });
        setTimeout(function () {
            heartbeat(sid)
        }, 10000)
    }


}

function rq_close() {
    for (var i = 0; i < sids.length; i++) {
        var sid = sids[i];
        socketManager.close({
            sid: sid
        }, function (ret, err) {
        });
    }
    sids = new Array();
}

function rq(data) {
    socketManager.createSocket({
        host: '180.186.38.211',
        port: 14000,
    }, function (ret, err) {
        var sid = ret.sid;
        if (ret) {
            // alert(JSON.stringify(ret));
            if (ret.state == 101) {
                sids.push(sid);
                socketManager.write({
                    sid: sid,
                    data: data,
                    base64: true
                }, function (ret, err) {
                    heartbeat(sid);
                });
            } else if (ret.state == 204) {
                sids.remove(sid)
            }
        } else {
//                    alert(JSON.stringify(err));
        }
    });

}

apiready = function () {
    socketManager = api.require('socketManager');

    getuserinfo();
    setInterval(getuserinfo, 5000);
};