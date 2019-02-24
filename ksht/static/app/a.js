var sendcount = 0;

function ajaxsend(voucherId,voucherType,targetUrl,storeLink,sliderToken,smsCode,vcsCode) {
    var terminalType = getTerminalType();

    $.ajax({
	        url:"//yzdh.suning.com/yzdh-web/voucher/sendVoucher.do",
	        dataType : "jsonp",
			jsonp : "callback",
			jsonpCallback : "callbackSendVoucherFun",
	        data:{voucherId:voucherId,voucherType:voucherType,couponGetSource:terminalType,sliderToken:sliderToken,smsCode:smsCode,vcsCode:vcsCode,detect:encodeURIComponent(bd.rst())},
	        success:function(data) {
	            if( data.resultCode == "0"){
	                window.location.href = "//yzdh.suning.com/yzdh-web/m/voucher/index.htm";
                }
            }
            });

}


function get() {
    sendcount = sendcount + 1;
    ajaxsend(2264, 1, '超市', 5, 199, 120, 'http://c.m.suning.com/channel/newCshi_index.html');
    if (sendcount <999) {
        setTimeout(function () {
            get()
        }, 4000);
    }
}

function send() {
    sendcount = 0;
    get()

}
send();

