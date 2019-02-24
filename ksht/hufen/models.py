from django.db import models
import django.utils.timezone as timezone
# Create your models here.
#互粉列表
class HufenHistory(models.Model):
    HufenId = models.CharField("互粉编号",unique=True, default="0_0", max_length=128)
    user1 = models.IntegerField("用户1", default=0)
    user2 = models.IntegerField("用户2", default=0)
    state = models.IntegerField("匹配状态", default=0)
    #0-匹配超时 1-匹配成功 2-双方不一致 3-服务器故障 4-互粉中主动终止 5-成功后取关
    bguser = models.IntegerField("背锅用户", default=0)
    errinfo = models.CharField("异常信息", default="NoError", max_length=256)
    hftime = models.DateTimeField("互粉时间",default = timezone.now)

#取关列表
class CancleHf(models.Model):
    CancelId = models.CharField("取关编号", unique=True, default="0_0", max_length=128)
    userid = models.IntegerField("被取关用户", default=0) #被取关用户id
    cancle_id = models.IntegerField("取关用户", default=0) #取关用户id
    cancel_time = models.DateTimeField("取关时间",default = timezone.now)

