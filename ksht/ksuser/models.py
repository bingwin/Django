import json

from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.timezone import now
# Create your models here.
class User(AbstractUser):
    choices_viplevel = (
        (0, "普通用户"),
        (1, "黄金会员"),
        (2, "白金会员"),
        (3, "钻石会员"),

    )
    userid = models.BigIntegerField("用户ID",unique=True,default=0)
    integral = models.IntegerField("积分",default=0)
    credit = models.IntegerField("信用度",default=100)
    referee = models.ForeignKey("User",verbose_name="推荐人",null=True,blank=True,related_name="referees_set")
    reg_time = models.DateTimeField("注册时间",auto_now_add=True)
    validate = models.BooleanField("是否验证",default=False)
    isvip = models.BooleanField("是否是VIP",default=False)
    viptime = models.DateTimeField("VIP到期时间", null=True,blank=True)
    viplevel = models.IntegerField("VIP等级",default=0,choices=choices_viplevel)
    total_photo = models.IntegerField("推广作品数", default=0)
    total_like = models.IntegerField("获得喜欢总数",default=0)
    total_comment = models.IntegerField("获得评论总数", default=0)



    comment_deny = models.BooleanField("禁止评论",default=True)
    activetime = models.DateTimeField("最后一次活跃时间",auto_now=True)


    def info2json(self,_self=True):
        return json.dumps(
            {
                "userid": self.userid,
                "integral": self.integral,
                "credit": self.credit,
                "validate": self.validate,
                "refereecount":self.referees_set.count()
            }
        )

class TGUser(models.Model):
    user = models.ForeignKey(User, verbose_name="推广用户")
    owner_head = models.CharField(default="",max_length=256)
    tgtime = models.DateTimeField("推广时间")



class IntegralEvent(models.Model):

    EVENT_like = 1
    EVENT_blike = 2
    EVENT_comment = 3
    EVENT_bcomment = 4
    EVENT_follow = 5
    EVENT_bfollow = 6
    EVENT_recharge = 7
    EVENT_invite = 8
    EVENT_rmfx = 9
    EVENT_tg = 10
    EVENT_xd = 11
    EVENT_garbage = 12

    choices = (
        (EVENT_like,"点赞"),
        (EVENT_blike,"被点赞"),
        (EVENT_comment,"评论"),
        (EVENT_bcomment,"被评论"),
        (EVENT_follow,"关注"),
        (EVENT_bfollow,"被关注"),
        (EVENT_recharge,"充值积分"),
        (EVENT_invite,"邀请用户"),
        (EVENT_rmfx, "热门分析"),
        (EVENT_tg, "邀请用户"),
        (EVENT_xd, "下单"),
        (EVENT_garbage, "垃圾消息"),
    )
    type = models.IntegerField("事件类型",choices=choices)
    user = models.ForeignKey(User,verbose_name="积分变化的用户",null=True,blank=True)
    integral = models.IntegerField(verbose_name="积分变化",default=0)
    remark = models.CharField("备注",max_length=500,default="")
    time =  models.DateTimeField("时间",auto_now=True)
