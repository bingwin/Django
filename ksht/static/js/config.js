/**
 * Created by miui on 2016/4/5.
 */
var W=W||{};

W.getRootPath=function(){
    //获取当前网址，如： http://localhost:8083/share/index.jsp
    var curWwwPath=window.document.location.href;
    //获取主机地址之后的目录，如： /share/meun.jsp
    var pathName=window.document.location.pathname;
    var pos=curWwwPath.indexOf(pathName);
    //获取主机地址，如： http://localhost:8083
    var localhostPaht=curWwwPath.substring(0,pos);
    //获取带"/"的项目名，如：/share
    var projectName = pathName.substring(0, pathName.substr(1).indexOf('/') + 1);
    return (localhostPaht + projectName);
};
W.url=W.getRootPath();
W.getQueryString=function(str){
    var re = new RegExp("[&,?]"+str + "=([^//&]*)", "i");
    var a = re.exec(document.location.search);
    if (a == null)
        return "";
    return a[1];
};
W.isEmpty=function(value){
    if(value==null||value==undefined||String(value).replace(/(^\s*)|(\s*$)/g,"").length<=0){
        return true;
    }
    if(typeof(value)=="object"){
        for (var item in value){
            return false;
        }
        return true;
    }
};