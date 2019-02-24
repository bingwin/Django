__author__ = 'shiwei'
from django.conf.urls import *
import ksuser.views
from django.template import Template

urlpatterns = [
    #url(r"tguser$", ksuser.views.tguser, name="tguser"),
    #url(r"index$", ksuser.views.index, name="index"),
    url(r"profile$", ksuser.views.profile, name="profile"),
    url(r"check$", ksuser.views.check, name="check"),
    url(r"check2$", ksuser.views.check2, name="check2"),
    url(r"check_start$", ksuser.views.check_start, name="check_start"),
    url(r"sign$", ksuser.views.sign, name="sign"),
    url(r"modpass$", ksuser.views.modpass, name="modpass"),
    url(r"jfcz$", ksuser.views.jfcz, name="jfcz"),
    url(r"tg$", ksuser.views.tg, name="tg"),
    url(r"cxcount$", ksuser.views.cxcount, name="cxcount"),
]
