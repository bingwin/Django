import hashlib
import urllib.parse
import requests
import json
import random
import hprose
import time
from random import choice




class gifshow_base():
    def __init__(self, version=None):
        self.host = None

        self.hosts =  ["api.gifshow.com" ,
                       "api.ksapisrv.com",]
        self.proxy = None
        self.versions = {
            "4.46.1.1739": ("4.46", "4.46.1.1739", "3c2cd3f3", "382700b563f4"),
            "4.47.0.1852": ("4.47", "4.47.0.1852", "3c2cd3f3", "382700b563f4"),
            "4.43.0.1228": ("4.43", "4.43.0.1228", "3c2cd3f3", "382700b563f4"),
            "4.48.0.1930": ("4.48", "4.48.0.1930", "3c2cd3f3", "382700b563f4"),
            "4.50.0.2271": ("4.50", "4.50.0.2271", "3c2cd3f3", "382700b563f4"),
            "4.53.3.3098": ("4.53", "4.53.3.3098", "3c2cd3f3", "382700b563f4"),
            "5.2.0.4649": ("5.2", "5.2.0.4649", "3c2cd3f3", "382700b563f4"),
        }
        self.headers = {
            "Connection": "Keep-Alive",
            "Accept-Language": "zh-cn",
            "User-Agent": "kwai-android",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Encoding": "gzip",
        }
        self.method = "POST"
        self.defaultparams = (
            "salt", "ud", "token", 'app', 'appver', 'c', 'client_key', 'country_code', 'did', 'language', 'lat', 'lon',
            'mod', 'net', 'oc', 'os', 'sys', 'ver')
        self.params = dict()

        self.urlparams = ['app', 'appver', 'c', 'country_code', 'did', 'language', 'lat', 'lon', 'mod', 'net', 'oc',
                          'sys', 'ud', 'ver']
        self.postparams = ['client_key', 'token', 'os']

        self.timeout = 10

        if version == None:
            self.version = self.versions["4.53.3.3098"]
        else:
            self.version = self.versions[version]

        self.token_client_salt = None

    def setDefaultValue_ver(self):
        return self.version[0]

    def setDefaultValue_appver(self):
        return self.version[1]

    def setDefaultValue_client_key(self):
        return self.version[2]

    def setDefaultValue_salt(self):
        return self.version[3]

    def setDefaultValue_ud(self):
        return "0"

    def setDefaultValue_token(self, ):
        return ""

    def setDefaultValue_app(self):
        return "0"

    def setDefaultValue_c(self):
        return "GENERIC"

    def setDefaultValue_country_code(self):
        return "CN"

    def setDefaultValue_did(self):
        return "ANDROID_"+ hashlib.md5(str(self.params['ud']).encode()).hexdigest()[0:16].upper()


    def setDefaultValue_language(self):
        return "zh-cn"

    def setDefaultValue_lat(self):
        return "0"

    def setDefaultValue_lon(self):
        return "0"

    def setDefaultValue_mod(self):
        return "ONEPLUS(A0001)"

    def setDefaultValue_net(self):
        return "WIFI"

    def setDefaultValue_oc(self):
        return "GENERIC"

    def setDefaultValue_os(self):
        return "android"

    def setDefaultValue_sys(self):
        return "ANDROID_4.4.2"

    def setDefaultValues(self):
        for name in self.defaultparams:
            if not name in self.params.keys():
                value = getattr(self, "setDefaultValue_" + name)()
                self.params[name] = value

    def clear(self):
        self.params.clear()

    def gethost(self):
        if self.host != None:
            return self.host
        else:
            return random.choice(self.hosts)

    def getsign(self):
        param = []
        param.extend(self.urlparams)
        param.extend(self.postparams)
        param2 = []

        for name in param:
            if name != "sig":
                param2.append(name + "=" + self.params[name])

        param2 = "".join(sorted(param2)) + self.params['salt']
        md5 = hashlib.md5(param2.encode()).hexdigest()
        self.sig = md5

    def geturlparam(self):
        urlparams = self.urlparams
        urlparam = {}
        for name in urlparams:
            value = self.params[name]
            urlparam[name] = value
        return urllib.parse.urlencode(urlparam)

    def getpostparam(self):
        postparams = self.postparams
        # random.shuffle(urlparams)
        postparam = {}
        for name in postparams:
            value = self.params[name]
            postparam[name] = value
        return urllib.parse.urlencode(postparam) + "&sig=" + self.sig + "&"

    def seturl(self, url):
        self.url = url
        return self

    def setmethod(self, method):
        self.method = method
        return self

    def addurlparam(self, **kargs):
        for n, v in kargs.items():
            self.params[n] = str(v)
            if not n in self.urlparams:
                self.urlparams.append(n)
        return self

    def addpostparam(self, **kargs):
        for n, v in kargs.items():
            if n == "token":
                self.settoken(v)
            else:
                self.params[n] = str(v)

            if not n in self.postparams:
                self.postparams.append(n)
        return self

    def send(self):

        self.setDefaultValues()
        self.getsign()
        if self.proxy  == None:
            proxies = None
        else:
            proxies = {
                "http": self.proxy ,
                "https": self.proxy ,
            }
        url = 'http://'+self.gethost()+'/' + self.url + "?" + self.geturlparam()
        if self.token_client_salt:
            self.params["__NStokensig"] = hashlib.sha256((self.sig + self.token_client_salt).encode()).hexdigest()
            self.postparams.append("__NStokensig")
        post = self.getpostparam()
        r = requests.post(url, data=post, headers=self.headers, proxies=proxies,timeout=self.timeout)
        return r.content

    def send_text(self):
        return self.send().decode()

    def send_json(self):
        return json.loads(self.send_text())

    def settoken(self, token):
        try:
            self.params['ud'] = token.split("-")[1]
            self.params["token"] = token
        except:
            self.params['ud']="0"
            self.params["token"] = ""
        return self


    def settoken_client_salt(self,token_client_salt):
        self.token_client_salt = token_client_salt
        return self


    def sethost(self, host):
        self.host = host
        return self
    def setproxy(self, proxy):
        self.proxy = proxy
        return self

class gifshow(gifshow_base):

    def follow(self, touid, page_ref=None, **kargs):

        self.seturl("rest/n/relation/follow")
        # ks://addfriend 1
        # ks://users/following/6816038 3
        if page_ref == None:
            pageref = random.randint(1, 22)
        else:
            pageref = page_ref
        self.addpostparam(page_ref=pageref, touid=touid, act_ref="", referer="", ftype=1)
        self.addpostparam(**kargs)
        result = self.send_json()
        return result

    def unfollow(self, touid, page_ref=None, **kargs):
        self.seturl("rest/n/relation/follow")
        # ks://addfriend 1
        # ks://users/following/6816038 3
        if page_ref == None:
            pageref = random.randint(1, 22)
        else:
            pageref = page_ref
        self.addpostparam(page_ref=pageref, touid=touid, act_ref="", referer="", ftype=2)
        self.addpostparam(**kargs)
        result = self.send_json()
        return result

    def rest_n_relation_fol(self, touid, **kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/relation/fol")
        self.addpostparam(touid=touid, ftype=1)
        return self.send_json()

    def rest_n_feed_profile(self, user_id,count=30, **kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/feed/profile")
        self.addpostparam(count=count, pcursor="", user_id=user_id, referer="", mtype=2, lang="zh")
        return self.send_json()

    def rest_n_user_search(self,user_name,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/user/search")
        self.addpostparam(user_name=user_name,page=1)
        return self.send_json()

    def register_email(self,email,userName,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/user/register/email")
        self.addurlparam(ud="41315")
        self.addpostparam(gender="U",userName=userName,password="",email=email)
        return self.send_json()

    def user_profile_v2(self,user,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/user/profile/v2")
        self.addpostparam(user=user)
        return self.send_json()

    def live_startPlay(self,author,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/live/startPlay/v2")
        self.addpostparam(author=author,exp_tag="")
        return self.send_json()

    def live_stopPlay(self,liveStreamId,**kargs):
        self.addpostparam(**kargs)
        self.sethost("live.gifshow.com")
        self.seturl("rest/n/live/stopPlay")
        self.addpostparam(liveStreamId=liveStreamId)
        return self.send_json()

    def live_like(self,liveStreamId,**kargs):
        self.addpostparam(**kargs)
        self.sethost("live.gifshow.com")
        self.seturl("rest/n/live/like")
        self.addpostparam(liveStreamId=liveStreamId,count=1)
        return self.send_json()

    def live_comment(self,liveStreamId,content,copy=False,**kargs):
        self.addpostparam(**kargs)
        self.sethost("live.gifshow.com")
        self.seturl("rest/n/live/comment")
        copy = "true" if copy else "false"
        self.addpostparam(content=content,liveStreamId=liveStreamId,copy=copy)
        return self.send_json()

    def photo_comment_list(self,user_id,photo_id,pcursor="",count=20,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/photo/comment/list")
        self.addpostparam(order="desc",pcursor=pcursor,ctype=1,user_id=user_id,photo_id=photo_id,count=count)
        return self.send_json()
    def photo_comment_add(self,user_id,photo_id,content,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/photo/comment/add")
        referer = "ks://photo/%s/%s/3/1_a/1541574338726342658_h80#addcomment"%(user_id,photo_id)
        self.addpostparam(content=content,reply_to="",user_id=user_id,referer=referer,photo_id=photo_id,copy=0)
        return self.send_json()

    def photo_like(self,user_id,photo_id,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/photo/like")
        referer = "ks://photo/%s/%s/3/1_a/1568350775795728384_n80#doublelike"%(user_id,photo_id)
        self.addpostparam(cancel=0,user_id=user_id,referer=referer,photo_id=photo_id)
        return self.send_json()

    def photo_click(self,user_id,photo_id,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/clc/click")
        # userid = random.randint(1,4000000000)
        # s = hashlib.md5(str(userid).encode()).hexdigest()
        # token = "%s4%s-%d"%(s[0:12],s[13:32],userid)
        # self.settoken(token)
        data = "%s_%s_p5"%(user_id,photo_id)
        self.addpostparam(downs="",data=data)

        return self.send_json()

    def photo_info(self,photoIds,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/photo/info")
        if type(photoIds) == list:
            photoIds = [str(i) for i in photoIds]
            photoIds = ",".join(photoIds)
        self.addpostparam(photoIds=photoIds)
        return self.send_json()

    def photo_likeshow2(self,photo_id,pcursor="",**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/photo/likeshow2")
        self.addpostparam(photo_id=photo_id,pcursor=pcursor)
        return self.send_json()


    def feed_list(self,count=20,page=1,type=7,pcursor="",**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/feed/list")
        self.addpostparam(count=count,page=page,pcursor=pcursor,pv="false",type=type)
        return self.send_json()


    def message_dialog(self,count=20,page=1,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/message/dialog")
        self.addpostparam(count=count,page=page)
        return self.send_json()

    def authStatus(self,**kargs):
        self.addpostparam(**kargs)
        self.seturl("rest/n/live/authStatus")
        return self.send_json()




def GetMiddleStr(content,startStr,endStr):
    startIndex = content.find(startStr)
    if startIndex>=0:
        startIndex += len(startStr)
    endIndex = content.find(endStr,startIndex)
    return content[startIndex:endIndex]



class CheckError(Exception):
    def __init__(self,code, msg):
        self.code = code
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class action_gifshow_like():
    def check(self,*args,**kwarg):
        return

    def format(self,photo,*args,**kwarg):
        userid = int(GetMiddleStr(photo+"&","userId=","&"))
        photoid = int(GetMiddleStr(photo+"&","photoId=","&"))
        if userid<1 and photoid<1:
            CheckError(-1,"链接异常")
        return {"userid":userid,"photoid":photoid}

    def getcount(self,userid,photoid,*args,**kwarg):
        userinfo = gifshow().rest_n_feed_profile(userid,count=100)
        def getphotoidcount(feeds,photoid):
            for feed in feeds:
                if feed['photo_id'] == photoid:
                    return feed['like_count']
        return getphotoidcount(userinfo['feeds'],photoid)


    def exe(self,userid,photoid,token,proxy,*args,**kwarg):

        try:
            result = gifshow().settoken(token[1]).setproxy(proxy).photo_like(userid,photoid)
        except Exception as e:
            result = None
            pass

        return result

    def show(self,userid,photoid,*args,**kwarg):
        return  '''喜欢<a href="http://www.kuaishou.com/i/photo/lwx?userId=%s&photoId=%s" target="_black">%s-%s</a>'''%(userid,photoid,userid,photoid)




class action_gifshow_photocomment():
    #http://www.gifshow.com/i/photo/lwx?userId=86752451&photoId=943312486&cc=share_copylink&fid=6816038&et=1_a%2F1541574338726342658_h80


    def check(self,userid,*args,**kwarg):
        self.userinfo = gifshow().rest_n_feed_profile(userid)
        if self.userinfo['comment_deny'] =='1':
            raise CheckError(-1,"禁止评论！")

    def format(self,photo,content,*args,**kwarg):
        userid = int(GetMiddleStr(photo+"&","userId=","&"))
        photoid = int(GetMiddleStr(photo+"&","photoId=","&"))
        if userid<1 and photoid<1:
            CheckError(-1,"链接异常")
        _content = content.split("\r\n")
        content = []
        for v in _content:
            v =  v.strip()
            if  len(v) != 0 :
                content.append(v)
        return {"userid":userid,"photoid":photoid,"contents":content}


    def getcount(self,userid,photoid,*args,**kwarg):
        info = gifshow().photo_comment_list(userid,photoid)
        count = info['commentCount']
        return count

    def exe(self,userid,photoid,contents,token,proxy,*args,**kwarg):
        content = choice(contents)
        try:
            result =  gifshow().settoken(token[1]).setproxy(proxy).photo_comment_add(userid,photoid,content)
            # if token[0] > 0:
            #     client =  hprose.HproseHttpClient("http://120.27.35.91/api")
            #     client.followresult(userid,token[0],result)
        except Exception as e:
            result = None
            pass

        return result

    def show(self,userid,photoid,*args,**kwarg):
        return  '''评论<a href="http://www.kuaishou.com/i/photo/lwx?userId=%s&photoId=%s" target="_black">%s-%s</a>'''%(userid,photoid,userid,photoid)

class action_gifshow_click():
    def check(self,userid,photoid,*args,**kwarg):
        self.photo_info(photoid)

    def format(self,photo,*args,**kwarg):
        userid = int(GetMiddleStr(photo+"&","userId=","&"))
        photoid = int(GetMiddleStr(photo+"&","photoId=","&"))
        if userid<1 and photoid<1:
            CheckError(-1,"链接异常")
        return {"userid":userid,"photoid":photoid}

    def getcount(self,userid,photoid,*args,**kwarg):
        photoinfo = self.photo_info(photoid)
        return photoinfo["view_count"]

    def photo_info(self,photoid):
        result = gifshow().sethost("180.186.38.200").photo_info(photoid)
        if result["result"] !=1:
            if "error_msg" in result.keys():
                msg = result["error_msg"]
            else:
                msg = "异常错误"
            raise CheckError(result["result"],msg)
        return result["photos"][0]




    def exe(self,userid,photoid,*args,**kwarg):

        try:
            g = gifshow()
            g.timeout = (5,2)
            result = g.photo_click(userid,photoid)
        except Exception as e:
            result = None
            pass

        return result

    def show(self,userid,photoid,*args,**kwarg):
        return  '''<a href="http://www.kuaishou.com/i/photo/lwx?userId=%s&photoId=%s" target="_black">%s-%s</a>'''%(userid,photoid,userid,photoid)

class action_gifshow_fans():
    userinfo = None
    t = 0

    def setdata(self,*args,**kwarg):
        pass


    def check(self,userid,*args,**kwarg):
        self.userinfo = gifshow().rest_n_feed_profile(userid)
        if self.userinfo['privacy_user'] =='1':
            raise CheckError(-1,"隐私用户！")



    def format(self,userid,*args,**kwarg):
        userid = int(userid)
        userids = [ user["user_id"] for user in gifshow().settoken("a5eaa088fa464ca3a66184cd869671fb-257905927").rest_n_user_search(userid)["users"]]
        if not userid in userids:
            raise CheckError(-1,"用户不存在！")
        return {"userid":userid}

    def getcount(self,userid,*args,**kwarg):
        if self.userinfo ==None or (time.time() - self.t) > 1:
            self.userinfo = gifshow().rest_n_feed_profile(userid)
        count = self.userinfo['owner_count']['fan']
        self.userinfo =None
        return count

    def exe(self,userid,token,proxy,*args,**kwarg):
        try:
            result =  gifshow().settoken(token[1]).setproxy(proxy).follow(userid)
            if token[0] > 0:
                client =  hprose.HproseHttpClient("http://120.27.35.91/api")
                client.followresult(userid,token[0],result)
        except Exception as e:
            result = None
            pass
        return result
    def show(self,userid,*args,**kwarg):
        return  str(userid)


import re
def getproxys(api,count):
    # if not re.match('^(http://){0,1}[A-Za-z0-9][A-Za-z0-9\-\.]+[A-Za-z0-9]\.[A-Za-z]{2,}[\43-\176]*$',api):
    #     print("代理API不规范")
    #     return []

    i = api.find("%count%")
    if i>0:
        api = api[:i]+ str(count)+api[i+7:]
    content =  requests.get(api,timeout=5).text
    content = content.split('\r\n')
    ips = []
    for ip in content:
        ip = ip.strip()
        if len(ip)>0:
            ips.append(ip)
    ips = list(set(ips))
    return ips


# s = []
# p = ""
# while True:
#     result =  gifshow().photo_likeshow2(2274584761, p)
#     p = result["pcursor"]
#     print( p )
#     for user in result["likers"]:
#         s.append(
#             user["user_id"]
#         )
#     if p == "no_more":
#         break
# print(s)

# token = "b38a25b0379f44cb9e110baa2a8d5661-269482514"
# print(gifshow().settoken(token).photo_like(117796659,2247457094))
# print(gifshow().settoken(token).follow(117796659))
#print(gifshow().sethost("180.186.38.200").rest_n_feed_profile("468748",count=100))
# ips = getproxys("http://www.httpsdaili.com/api.asp?key=20160223093333112&getnum=50")
# print(len(ips),ips)
#token= "1a4dc6cdb9414cf2978be2ee422c099d-286324786"
#r = gifshow().settoken(token).live_startPlay("164186883")
#print(r['liveStreamId'])
#print(gifshow().settoken(token).live_like(r['liveStreamId']))
#print(gifshow().settoken(token).live_comment(r['liveStreamId'],"222222222222222222222"))
#print(gifshow().register_email("qwe22qweq2@163.com"))
#print(gifshow().follow(471111111,token="1a053129a4824dfb9e047ff48e7814ee-262239722"))
# print(gifshow().unfollow(275256314,token="b9ae59304b5742b4ad13406085fe1f50-264876848"))
#print(gifshow().rest_n_relation_fol(265433234,token="b9ae59304b5742b4ad13406085fe1f50-264876848"))
# print(gifshow().rest_n_feed_profile("275256314")['owner_count']['fan'])

# 2c2f9fd359a1493eba6a484077cf71e7-6816038
#
# for i in range(0,100000):
#     try:
#         r = gifshow()\
#         .settoken("04f9983ef0064e1f9b6c0e0d047dbdfb-140153961")\
#         .seturl("rest/photo/like")\
#         .setproxy("121.42.154.166:80")\
#         .register_email("caax4@qq.com","aqsacas12xx")
#         print(r)
#     except Exception as e :
#         pass
#
# #
#=1495693686671
#2540355768
# import time
# print(int(time.time()*1000))
# print(gifshow().photo_info("2547108938")["photos"])
# c = int(time.time()*1000) - gifshow().photo_info("2544131862")["photos"][0]["timestamp"]
# print(c)
# print(7*24*60*60*1000)
# print(gifshow().user_profile_v2())

# for i in range(0,10000):
# print(gifshow().settoken("b28faa63d39444c4a414b0430915a765-34675922").user_profile_v2(707))
# print(gifshow().settoken("9c1ef396863c42a999724eb6ed5c607f-41913181").follow(707))
