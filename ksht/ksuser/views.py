import time
import json
import random
import datetime
import threading
from collections import OrderedDict

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.contrib import auth
from django.db.models import F, Q

from GIFShowCaptcha import Captcha as GIFShowCaptcha
from ksuser.models import User, IntegralEvent
from gifshowapi import gifshow
from ksht import settings
from django.contrib.auth.decorators import login_required
from ksuser.models import TGUser
from django.utils import timezone
from datetime import timedelta

tqksids = []



# Create your views here.

@csrf_exempt
def index(request):
    return render(request, "index.html")

@csrf_exempt
def login(request):
    return render(request, "ksuser/login.html")

@csrf_exempt
def kslogin(request):
    if not request.POST:
        return render(request, "ksuser/kslogin.html")
    else:

        next = request.GET.get("next", "/")
        ksid = int(request.POST.get("ksid", "0"))
        password = request.POST.get("password", "")


        if ksid == 725134:
            return JsonResponse({"err": -1, "msg": "你不是神秘人吧？"})

        settings.redisconn.set("ksuserlist:%d" % ksid, ksid)  # 方便查询用户是否存在
        request.session["gifshowusercheck"] = False
        user = User.objects.filter(userid=ksid).first()
        if not user: #新用户
            if password != "":
                return JsonResponse({"err": -2, "msg": "密码错误"})
            #限制快手号
            try:
                result = gifshow().settoken("0-0").user_profile_v2(ksid)
            except:
                return JsonResponse({"err": -1, "msg": "登录异常，请重试"})
            try:
                result = result["userProfile"]
            except:
                return JsonResponse({"err": -1, "msg": "用户不存在"})
            owner_count = result["ownerCount"]
            if (owner_count["fan"] < settings.LoginMinFanCount or owner_count["follow"] < settings.LoginMinFanCount):
                return JsonResponse({"err": -1, "msg": "粉丝数和关注数都要大于%s才能使用本平台！" % settings.LoginMinFanCount})

            user = User()
            user.username = "User_%s" % ksid
            user.set_password("")
            user.userid = ksid
            user.integral = 200
            user.save()
        elif password != "":
            if not user.check_password(password):
                return JsonResponse({"err": -2, "msg": "密码错误"})
            else:
                request.session["gifshowusercheck"] = True

        auth.login(request, user)

        if next == "/photo/bofan" or next == "/bofan":
            next = "/"
        return JsonResponse({"err": 0, "msg": "登陆成功", "url": next})





@csrf_exempt
@login_required(login_url="/kslogin?next=user/modpass")
def modpass(request):
    if not request.session.get("gifshowusercheck", False):
        return JsonResponse({"err": -2, "msg": "没有验证！"})
    password = request.POST.get("password", "")
    request.user.set_password(password)
    request.user.save()
    return JsonResponse({"err": 0, "msg": "修改成功"})


@login_required(login_url="/kslogin?next=user/profile")
def profile(request):
    count_like = 0
    count_comment = 0
    photos = Photo2.objects.filter(user=request.user)
    for p in photos:
        count_like += p.htcount_like
        count_comment += p.htcount_comment


    count_referee = request.user.referees_set.count()

    today = timezone.now() #按时区的有问题，先直接用机器时间
    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%d")

    sign = settings.redisconn.exists("sign:%s:%s" % (today, request.user.id))
    sign_continuity = settings.redisconn.get("sign:%s:%s" % ("continuity", request.user.id))
    return render(request, "ksuser/profile.html", {"count_photo": len(photos)+request.user.total_photo,
                                                   "count_like": count_like+request.user.total_like,
                                                   "count_comment": count_comment+request.user.total_comment,
                                                   "count_referee": count_referee,
                                                   "sign": sign,
                                                   "sign_continuity": sign_continuity

                                                   })


def showuser(request, userid):
    if User.objects.filter(userid=userid).exists():
        request.session["tguserid"] = userid

    return render(request, "u2.html", {"userid": userid})


def code(request):
    figures = [2, 3, 4, 5, 6, 7, 8, 9]
    ca = Captcha(request)
    ca.words = [''.join([str(random.sample(figures, 1)[0]) for i in range(0, 4)])]
    ca.type = 'word'
    ca.img_width = 60
    ca.img_height = 30
    return ca.display()


# #方便查询用户是否存在
# for user in  User.objects.all() :
#     settings.redisconn.set("ksuserlist:%d" % user.userid, user.userid)
@csrf_exempt
@login_required(login_url="/kslogin?next=/user/check")
def check(request):
    captcha = GIFShowCaptcha(request)
    if request.POST.get("restart", "0") == "1":
        captcha.delcode()
        _captcha = captcha.getcode()
    else:
        _captcha = captcha.getcode()

    if request.method != "POST":
        return render(request, 'ksuser/check.html', {"captcha": _captcha})
    else:
        return JsonResponse(_captcha)


def check2(request):
    userid = request.GET.get("userid", "")
    photoid = request.GET.get("photoid", "")
    photourl = request.GET.get("photourl", "")
    code = request.GET.get("code")
    return render(request, 'ksuser/check2.html', {"userid": userid,
                                                  "photoid": photoid,
                                                  "code": code,
                                                  "photourl": photourl,
                                                  })


@csrf_exempt
def check_start(request):
    if request.method != "POST":
        return HttpResponse()
    else:
        code = request.POST.get("code")
        captcha = GIFShowCaptcha(request)
        status = captcha.validate(code)
        if status:
            captcha.delcode()
            request.session["gifshowusercheck"] = True
            if not request.user.validate:
                if "tguserid" in request.session.keys() and request.session["tguserid"] != request.user.userid:
                    tguser = User.objects.get(userid=request.session["tguserid"])
                    tguser.integral = F("integral") + request.site.jifen_tg
                    tguser.save()

                    eventobj = IntegralEvent()
                    eventobj.type = IntegralEvent.EVENT_tg
                    eventobj.user = tguser
                    eventobj.integral = request.site.jifen_tg
                    eventobj.remark = "邀请用户%s" % request.user
                    eventobj.save()

                    request.user.referee = tguser

                request.user.validate = True

                request.user.save()

        return JsonResponse({"status": status})


def logout(request):
    request.user.validate = False
    auth.logout(request)
    return HttpResponseRedirect("/")




@csrf_exempt
@login_required(login_url="/kslogin?next=/user/sign")
def sign(request):
    site2, _ = Site2.objects.get_or_create(id=1)

    if request.method != "POST":
        sign_wechat =  random.choice(site2.sign_wechat.split(","))
        return render(request,"ksuser/sign.html",{"sign_wechat": sign_wechat})
    else:

        if not request.session.get("gifshowusercheck", False):
            return JsonResponse({"err": -2, "msg": "没有验证！"})
        today = timezone.now()  # 按时区的有问题，先直接用机器时间
        today = datetime.datetime.now()
        yesterday = today + timedelta(days=-1)
        today = today.strftime("%Y-%m-%d")
        yesterday = yesterday.strftime("%Y-%m-%d")



        try:
            _type = int(request.POST.get("type"))
        except:
            _type = 1
        key = request.POST.get("key")


        if _type == 2:
            #公众号签到

            if key != site2.sign_key:
                return JsonResponse({"err": -3, "msg": "口令错误，请查看朋友圈的口令，口令会每日更新！"})
            else:
                if settings.redisconn.setnx("sign_wechat:%s:%s" % (today, request.user.id),1) == 0:
                    return JsonResponse({"err": -1, "msg": "今日已经签到！"})
                else:
                    jf = 100
                    User.objects.filter(id=request.user.id).update(integral=F("integral")+jf)
                    return JsonResponse({"err": 0, "msg": "签到成功！奖励%s积分！" % (jf)})
        elif _type ==1:

            xy = 1
            if settings.redisconn.exists("sign:%s:%s" % (today, request.user.id)):
                return JsonResponse({"err": -1, "msg": "今日已经签到！"})
            else:

                if settings.redisconn.setnx("sign:%s:%s" % (today, request.user.id), "1"):
                    settings.redisconn.incr("sign:continuity:%s" % request.user.id)
                    continuity = True
                else:
                    settings.redisconn.set("sign:continuity:%s" % request.user.id, "1")
                    continuity = False




                if  request.user.viplevel == 0:
                    jf = 50
                elif request.user.viplevel == 1:
                    jf = 200
                elif request.user.viplevel == 2 :
                    jf = 1000
                elif request.user.viplevel == 3:
                    jf = 1000
                else:
                    jf = 50

                request.user.integral = F("integral") + jf
                request.user.credit = F("credit") + xy
                request.user.save()

                if request.user.viplevel == 0 :
                    return JsonResponse({"err": 0, "msg": "签到成功！奖励%s积分，%s信誉值,开通会员后有更多签到奖励积分！" % (jf, xy)})
                else:
                    return JsonResponse({"err": 0, "msg": "签到成功！奖励%s积分，%s信誉值！" % (jf, xy)})
        else:
            return JsonResponse({"err": 0, "msg": "异常错误，请联系管理员"})



def tg(request):
    tgusers = TGUser.objects.filter(tgtime__gte=datetime.datetime.now()).all()

    jf = tgusers.count()*100
    return render(request, 'ksuser/tg.html',{"tgusers":tgusers,"jf":jf})

def jfcz(request):
    return render(request,"ksuser/jfcz.html")

def cxcount(request):
    return render(request,"ksuser/cxcount.html")



