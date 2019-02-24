import os
import sys


# 待解决问题

# 0.绑定两个用户进行的状态，在服务器保存，增加超时的协程，时间超过未进入下一状态则超时
# 0.5 用户传递的信息不能相信，由服务器主动判断
# 1.子线程在对pairs排序时，主线程不能对pairs进行增删改的操作，同一个用户不能同时对同一个变量在多个线程进行增删操作,匹配进程与超时进程对于pairs的访问如何上锁控制临界情况（超时的同时匹配到）
# 2.超时机制在后台实现
# 3.实现断线重传机制
# 4.改websocket为socket，在登录快手联盟之后保持socket连接
# 4.1 用户的互斥登录，抢占下线
# 5 按照信誉值高低匹配，如果超过某个阈值则不能匹配，下一轮匹配时增大阈值
# 6 信誉值相同则后点击确认互粉的用户先点关注
# 7 排序标准不一定只根据信誉值，重新定义变量保存该值

# Time:2017-11-19 Author:JiangShuai


sys.path.append("/home/js/Desktop/KS-WHLM/ksht/") #windows环境不用管 linux是应用的路径
os.environ['DJANGO_SETTINGS_MODULE'] = 'ksht.settings'  # 项目的settings
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.contrib.sessions.models import Session
from ksuser.models import User
from hufen.models import HufenHistory
from hufen.models import CancleHf

#上面过程是引用Django的ORM模型



import time
import datetime
import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import threading
import json

#线程池处理并发请求
# from tornado.concurrent import run_on_executor
# from concurrent.futures import ThreadPoolExecutor


#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

users = dict()  # 所有登陆用户信息 {user:self}
pairs = dict()  # 待配对用户信息 {user:self}
pairing = dict()  # 正在匹配的成对用户信息，{key,[self1,self2,step]}
cost = 5 #互粉成功扣除积分

# 每个用户在互粉大厅中的状态HufenPos
# 0-无任何操作
# 1-正在匹配中
# 2-正在互粉中
# 互粉过程中的状态step:
# 0-双方都点击确认
# 1-D去快手关注 或未关注-9-双方互粉失败
# 2-D确认已关注 或未确认-9
# 3-G去快手确认 或未确认-9
# 4-G确认被关注 或未确认-9
# 5-G去快手关注 或未关注-9
# 6-G确认已关注 或未确认-9
# 7-D确认被关注 或未确认-9
# 8-双方互粉成功
# 互粉正常情况:
# pair: 			点击我要互粉
# dopair: 		点击确认互粉
# repair: 		重新匹配/换个老铁
# 	state:
# 		firstrepair:	互粉开始时换人
# 		other:		互粉过程中换人
# ConfirmPairFirst:	低用户选择去关注匹配用户
# ConfirmFocusFirst：	低信誉值用户选择已经关注匹配用户
# CheckFocusFirst： 	高信誉值用户选择去快手确认对方是否关注
# ConfirmFocusPre：	高信誉值用户选择对方已经关注自己
# ConfirmFocusSecond：	高信誉值用户选择去快手关注对方
# ConfirmSuccessFirst：	高信誉值用户选择已经关注对方
# CheckFocusSecond：	低信誉值用户选择去快手确认对方是否关注
# ConfirmSuccessSecond：	低信誉值用户选择对方已经关注自己

# 互粉终止情况
# NoConfirmPairFirst:	低用户取消/否定去关注匹配用户
# 	state:
# 		cancel:	取消
# 		deny:	否定
# NoConfirmFocusFirst：	低信誉值用户取消/否定已经关注匹配用户
# 	state:		同上
# NoCheckFocusFirst： 	高信誉值用户取消去快手确认对方是否关注
# NoConfirmFocusPre：	高信誉值用户取消/否定对方已经关注自己
# 	state:		同上
# NoConfirmFocusSecond：	高信誉值用户取消/否定去快手关注对方
# 	state:		同上
# NoConfirmSuccessFirst：	高信誉值用户取消/活动已经关注对方
# 	state:		同上
# NoCheckFocusSecond：	低信誉值用户取消去快手确认对方是否关注
# NoConfirmSuccessSecond：低信誉值用户取消/否定选择对方已经关注自己
# 	state:		同上
# 互粉终止情况
#



lock = threading.Lock()
# value = 100
# delay = 1
# wait_time = 5

# 状态1 2 3的互粉列表更新
def HufenFail123(self,sta,info):
    if HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid).first():
        if sta == 3:
            HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid) \
                .update(state=sta,errinfo=info)
        else:
            HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid) \
                .update(state=sta)
    elif HufenHistory.objects.filter(user2=self.user.userid, user1=self.pairuser.userid).first():
        if sta == 3:
            HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid) \
                .update(state=sta, errinfo=info)
        else:
            HufenHistory.objects.filter(user2=self.user.userid, user1=self.pairuser.userid) \
                .update(state=sta)

# 状态0 4 5的互粉列表更新
def HufenFail045(self,sta,bgu):
    if HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid).first():
        HufenHistory.objects.filter(user1=self.user.userid, user2=self.pairuser.userid) \
            .update(state=sta,bguser=bgu)
    elif HufenHistory.objects.filter(user2=self.user.userid, user1=self.pairuser.userid).first():
        HufenHistory.objects.filter(user2=self.user.userid, user1=self.pairuser.userid) \
            .update(state=sta,bguser=bgu)


def get_key(self):
    first = self.user.userid
    second = self.pairuser.userid
    if self.user.userid > self.pairuser.userid:  # first 代表编号小的用户Id
        first = self.pairuser.userid
        second = self.user.userid
    key = str(first) + '_' + str(second)
    return key

def ServerError(self,info):
    message = json.dumps({"error": "server"})
    self.write_message(message)
    HufenFail123(self,3,info)

# 互粉一方终止时提醒对方
def TipForError(self,key,message):
    # pairing[key][2] = 9
    self.HufenPos = 0
    del pairing[key]
    HufenFail045(self,4,self.user.userid)
    if self.pairuser in users:
        users[self.pairuser].HufenPos = 0
        users[self.pairuser].write_message(message)
    else:
        ServerError(self,"用户：" + self.user.username + "在会话状态：" + str(pairing[key][2]) + "终止互粉时，用户：" \
                    + self.pairuser.username + "不在用户表中")

def TipForChange(self):
    HufenRate(self)
    self.HufenPos = 1  # 进入匹配状态
    if self.user not in pairs:
        self.pairtime = 0  # 初始状态为0
        if lock.acquire():
            pairs[self.user] = self  # 将该用户添加进待匹配字典中
        lock.release()
    else:
        self.pairtime = 0
    # 告知与该用户匹配的用户：互粉结束
    message = json.dumps({
        "action": "errorpair",
        "state": "change"})
    # 判断目标用户是否还存在
    if self.pairuser in users:
        # 重置对方的状态
        users[self.pairuser].HufenPos = 0
        users[self.pairuser].write_message(message)
    else:
        ServerError(self, "某用户选择换一个老铁时 用户:" + self.pairuser.username + "不在用户表中！")

# 计算互粉总次数与互粉率
def HufenRate(self):
    # 匹配总次数
    self.totletime = len(HufenHistory.objects.filter(user1=self.user.userid)) + \
                     len(HufenHistory.objects.filter(user2=self.user.userid))
    # 互粉成功次数
    suctime = len(HufenHistory.objects.filter(user1=self.user.userid, state=1)) + \
              len(HufenHistory.objects.filter(user2=self.user.userid, state=1))
    if self.totletime:
        self.sucrate = float(suctime / self.totletime)
    else:
        self.sucrate = 0


# 待匹配队列处理线程
class HufenPair(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.HufenPairThread()

    def HufenPairThread(self):
        global pairs
        error = json.dumps({"error": "nopair"})
        lis_f = []  # 记录每一轮没匹配到的用户，增加轮数，下一轮清空
        while True:
            # 按照信誉值降序排序
            # 对pairs上锁
            if lock.acquire():
                dic = dict(sorted(pairs.items(), key=lambda d: d[0].credit, reverse=True))
            #释放锁
            lock.release()

            lis = list(dic.keys())
            lis_f.clear()
            if len(lis) < 2:
                # lis_f = lis #这是引用赋值，会相互影响
                lis_f = lis.copy() #拷贝一个副本
            while len(lis) >= 2:
                #没有匹配到过
                if (len(HufenHistory.objects.filter(user1=lis[0].userid,user2=lis[1].userid)) == 0) and \
                    (len(HufenHistory.objects.filter(user1=lis[1].userid, user2=lis[0].userid)) == 0):
                    first = lis[0].userid
                    second = lis[1].userid
                    if first > second:  # first 代表信誉值低的用户Id
                        first = lis[1].userid
                        second = lis[0].userid
                    ID = str(first) + '_' + str(second)
                    HufenHistory.objects.create(HufenId=ID,user1=lis[0].userid,user2=lis[1].userid,state=0)
                    pairs[lis[0]].pairuser = lis[1]  # 暂时保存待匹配的对方信息
                    pairs[lis[1]].pairuser = lis[0]  # 暂时保存待匹配的对方信息
                    # 向匹配双方发送对方的信息
                    message1 = json.dumps({
                        "action":"pair",
                        "username":lis[1].username,
                        "userid":lis[1].userid,
                        "photo":lis[1].total_photo,
                        "credit":lis[1].credit,
                        "totletime":pairs[lis[1]].totletime,
                        "sucrate":pairs[lis[1]].sucrate})
                    message2 = json.dumps({
                        "action": "pair",
                        "username": lis[0].username,
                        "userid": lis[0].userid,
                        "photo": lis[0].total_photo,
                        "credit": lis[0].credit,
                        "totletime": pairs[lis[0]].totletime,
                        "sucrate": pairs[lis[0]].sucrate})
                    pairs[lis[0]].write_message(message1)
                    pairs[lis[1]].write_message(message2)
                    pairs[lis[0]].HufenPos = 2 # 进入互粉状态
                    pairs[lis[1]].HufenPos = 2  # 进入互粉状态
                    print("匹配信息：user_" + lis[0].username + "匹配到 user_" + lis[1].username)
                    del pairs[lis[0]]
                    del pairs[lis[1]]
                    # 将已匹配的两个用户从未匹配列表中删除
                    if lis[0] in lis_f:
                        lis_f.remove(lis[0])
                    if lis[1] in lis_f:
                        lis_f.remove(lis[1])
                else:
                    print("匹配信息：user_" + lis[0].username + "已匹配过 user_" + lis[1].username)
                    if lis[0] not in lis_f:
                        lis_f.append(lis[0])
                    if lis[1] not in lis_f:
                        lis_f.append(lis[1])
                del lis[0]
                del lis[0] #列表序号自动补位
            if len(lis) == 1: #记录多出来的一个用户
                if lis[0] not in lis_f:
                    lis_f.append(lis[0])
            for user in lis_f: # 遍历的是列表，要删除元素的时候不能直接遍历字典pairs
                if user in pairs:
                    pairs[user].pairtime += 1 # 提升一个状态
                    if pairs[user].pairtime > 2: # 匹配循环超过3轮
                        users[user].HufenPos = 0 # 无操作状态
                        pairs[user].write_message(error)
                        del pairs[user]
            time.sleep(1)

# 正在匹配队列处理线程，此时双方都确认互粉，向低信誉值用户发送关注对方的消息
# class HufenDoPair(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#         self.HufenDoPairThread()
#
#     def HufenDoPairThread(self):
#         while True:
#             for key in pairing:
#                 if len(pairing[key]) == 2: # 必须两个互粉用户都在
#                     # dopairstate 为1表示用户愿意匹配
#                     if pairing[key][0].dopairstate == 1 and pairing[key][1].dopairstate == 1:
#                         self1 = pairing[key][0]
#                         self2 = pairing[key][1]
#                         self1.dopairstate = 0
#                         self2.dopairstate = 0
#                         # 相同信誉值时，后点确认互粉的先关注，立马能关注
#                         if self1.user.credit >= self2.user.credit: # 信誉值低先关注  self1先
#                             self1 = pairing[key][1]
#                             self2 = pairing[key][0]
#                         message1 = json.dumps({
#                             "action": "dopairfirst",
#                             "userid": self2.user.userid})
#                         message2 = json.dumps({
#                             "action": "dopairsecond",
#                             "userid": self1.user.userid,
#                             "state": "wait"})
#                         self1.write_message(message1)
#                         self2.write_message(message2)
#             time.sleep(1)正在匹配队列处理线程，此时双方都确认互粉，向低信誉值用户发送关注对方的消息

# class TimeOut(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#         self.SetTimeOut()
#
#     def SetTimeOut(self):
#         global users
#         global pairs
#         while True:
#             for handler in users:
#                 timer = users[handler] # 获取self
#                 if timer.timecheck:
#                     endtime = datetime.now()
#                     difftime = (endtime - timer.statime).seconds
#                     if difftime >= overtime:
#                         timer.timecheck = 0
#                         message1 = json.dumps({
#                             "action": "errorpair",
#                             "state": "waitovertime"})
#                         message2 = json.dumps({
#                             "action": "errorpair",
#                             "state": "workovertime"})
#                         # 超时则对方背锅
#                         HufenFail045(timer,0,timer.pairuser.userid)
#                         timer.write_message(message1)
#                         # 用户在互粉操作时超时
#                         if handler not in pairs:
#                             if timer.pairuser in users:
#                                 users[timer.pairuser].write_message(message2)
#                             else:
#                                 ServerError(timer,"OverTime")
#                             key = get_key(timer)
#                             if key in pairing:
#                                 del pairing[key]
#                         else:
#                             lock.acquire()
#                             del pairs[handler]
#                             lock.release()
#             time.sleep(1)


class HallHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        uid = self.get_argument("userid")
        if not uid:
            self.finish({"error":"no user"})
        else:
            self.set_secure_cookie("uid", uid)
            user = User.objects.filter(userid=int(uid)).first()
            if not user:
                self.render("hufen/hall2.html", userid=uid, integral=0, credit=0)
            else:
                self.render("hufen/hall2.html", userid=user.userid, integral=user.integral, credit=user.credit)



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.sqldata()
        indexuser = []
        indexuser.clear()
        result = User.objects.all()
        for user in result:
            indexuser.append([user.userid,user.username])
        self.render("hufen/index2.html",users = indexuser)

    def sqldata(self):
        User.objects.all().delete()
        User.objects.create(username="jiang", userid=693787653, integral=1320, credit=117)
        User.objects.create(username="幻影 哥", userid=707, integral=1000, credit=100)
        User.objects.create(username="怪咖", userid=710, integral=950, credit=95)
        User.objects.create(username="老公", userid=355918693, integral=860, credit=101)
        User.objects.create(username="如梦初醒", userid=341190109, integral=750, credit=105)
        User.objects.create(username="少帅", userid=25562825, integral=600, credit=109)
        User.objects.create(username="阿飞", userid=54638707, integral=550, credit=125)
        User.objects.create(username="微微", userid=209084552, integral=450, credit=130)
        User.objects.create(username="菩提心", userid=518885986, integral=300, credit=134)
        User.objects.create(username="紫枫", userid=387878617, integral=225, credit=129)
        User.objects.create(username="付老师", userid=692773471, integral=20000, credit=2000)

class HufenHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            message = json.dumps({"error":"no user","action":"no"})
            self.write_message(message)
        else:
            ksuser = User.objects.filter(userid=int(uid)).first()
            if ksuser:
                self.user = ksuser #保存用户信息
                self.pairuser = ksuser #初始化匹配用户信息
                # self.dopairstate = 0 # 初始匹配状态为0，用户两用户正式匹配
                self.pairtime = 0 # 匹配循环次数，用于判断匹配过程超时
                self.HufenPos = 0 # 匹配进度 0-无操作 1-匹配中 2-互粉中
                self.totletime = 0 #匹配总次数
                self.sucrate = 0 #互粉成功率
                # self.timecheck = 0 #是否开启计时
                # self.statime = datetime.now() # 初始化开始时间
                if ksuser not in users:
                    users[ksuser] = self # 新用户添加到用户字典中
                print("新用户：" + str(ksuser.userid) + "已登录本系统")
                print("所有用户：")
                for user in users:
                    print(user.userid)
            else:
                self.user = "#"

    def on_message(self, message):
        if message == "HeartBeat":
            print("欢迎用户:" + self.user.username + "回来!")
        else:
            cmd = json.loads(message);
            if "action" in cmd:
                #在无操作状态的用户点击开始互粉按钮
                if (cmd["action"] == "pair") and self.HufenPos == 0:
                    # 计算互粉总次数与互粉率
                    HufenRate(self)
                    if self.user not in pairs:
                        self.pairtime = 0 #初始状态为0
                        if lock.acquire():
                            pairs[self.user] = self #将该用户添加进待匹配字典中
                        lock.release()
                        self.HufenPos = 1 # 进入匹配状态
                #在互粉状态的用户点击确认互粉按钮
                elif (cmd["action"] == "dopair") and self.HufenPos == 2:
                    key = get_key(self) # 此时已经匹配了，pairuser已经更新
                    if key not in pairing: # 保存确认互粉的会话,不存在则创建
                        pairing[key] = [self]
                    elif self not in pairing[key]: # 已存在则添加用户
                        pairing[key].append(self)
                    if len(pairing[key]) == 2:  # 必须两个互粉用户都在
                        pairing[key].append(0)  # 记录会话状态，0-双方点击确认
                        # [DU,GU]
                        self1 = pairing[key][0]
                        self2 = pairing[key][1]
                        # 相同信誉值时，后点确认互粉的先关注，立马能关注
                        if self1.user.credit >= self2.user.credit:  # 信誉值低先关注  self1先
                            self1 = pairing[key][1]
                            self2 = pairing[key][0]
                            # [DU,GU]
                            pairing[key][0] = self1
                            pairing[key][1] = self2
                        message1 = json.dumps({
                            "action": "dopairfirst",
                            "userid": self2.user.userid})
                        message2 = json.dumps({
                            "action": "dopairsecond",
                            "userid": self1.user.userid,
                            "state": "wait"})
                        self1.write_message(message1)
                        self2.write_message(message2)
                # 重新匹配
                elif (cmd["action"] == "repair") and self.HufenPos == 0:
                    HufenRate(self)
                    self.HufenPos = 1 # 进入匹配状态
                    if self.user not in pairs:
                        self.pairtime = 0 #初始状态为0
                        if lock.acquire():
                            pairs[self.user] = self #将该用户添加进待匹配字典中
                        lock.release()
                    else:
                        self.pairtime = 0

                # 换个老铁 判断是否处于会话中 防止攻击
                elif (cmd["action"] == "change") and self.HufenPos == 2:
                    key = get_key(self)
                    # 有人点击了确认互粉
                    if key in pairing:
                        # 不处于互粉状态
                        if len(pairing[key]) != 3:
                            TipForChange(self)
                        else:
                            ServerError(self,"会话异常")
                    else:
                        TipForChange(self)


                # 低信誉值用户选择去快手关注匹配用户
                elif (cmd["action"] == "ConfirmPairFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        # 当前用户为DU
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                # 服务器状态为双方点击确认互粉
                                if pairing[key][2] == 0:
                                    # 进入下一步会话状态
                                    pairing[key][2] = 1
                                    message = json.dumps({"action": "doconfirmfirst"})
                                    self.write_message(message)
                                else:
                                    ServerError(self,"DU在会话状态为：" + str(pairing[key][2]) + "时不允许关注操作")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self,self.user.username + "在会话状态不为0时不是对应会话中的低用户，不能先发起关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")


                # 低信誉值用户选择已经关注匹配用户
                elif (cmd["action"] == "ConfirmFocusFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 1:
                                    pairing[key][2] = 2
                                    message = json.dumps({
                                        "action": "checkfocusfirst",
                                        "userid": self.pairuser.userid})
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message)
                                    else:
                                        ServerError(self, "低信誉值用户选择已经关注匹配用户时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时不允许确认已关注操作")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为1时不是对应会话中的低用户，不能确认自己已关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")


                # 高信誉值用户选择去快手确认对方是否关注
                elif (cmd["action"] == "CheckFocusFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 2:
                                    pairing[key][2] = 3
                                    message1 = json.dumps({"action": "doconfirmpre"})
                                    message2 = json.dumps({
                                        "action": "dofocusfirst",
                                        "state": "makeconfirm"})
                                    self.write_message(message1)
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message2)
                                    else:
                                        ServerError(self,"高信誉值用户选择去快手确认对方是否关注时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许确认对方是否关注")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为2时不是对应会话中的高用户，不能确认对方是否关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 高信誉值用户选择对方已经关注自己
                elif (cmd["action"] == "ConfirmFocusPre") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 3:
                                    pairing[key][2] = 4
                                    message1 = json.dumps({
                                        "action": "doconfirmsecond",
                                        "userid":self.pairuser.userid})
                                    message2 = json.dumps({
                                        "action": "dofocusfirst",
                                        "state": "makefocus"})
                                    self.write_message(message1)
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message2)
                                    else:
                                        ServerError(self,"高信誉值用户选择对方已经关注自己时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许确认对方已经关注")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为3时不是对应会话中的高用户，不能确认对方已经关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 高信誉值用户选择去快手关注对方
                elif (cmd["action"] == "ConfirmFocusSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 4:
                                    pairing[key][2] = 5
                                    message = json.dumps({"action": "dofocussecond"})
                                    message2 = json.dumps({
                                        "action": "dofocusfirst",
                                        "state": "dofocus"})
                                    self.write_message(message)
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message2)
                                    else:
                                        ServerError(self,"高信誉值用户选择去快手关注对方时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许关注对方")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为4时不是对应会话中的高用户，不能去关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")


                # 高信誉值用户选择已经关注对方
                elif (cmd["action"] == "ConfirmSuccessFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 5:
                                    pairing[key][2] = 6
                                    message = json.dumps({
                                        "action": "checkfocussecond",
                                        "userid":self.pairuser.userid})
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message)
                                    else:
                                        ServerError(self,"高信誉值用户选择已经关注对方时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许确认已经关注对方")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为5时不是对应会话中的高用户，不能确认已经关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 低信誉值用户选择去快手确认对方是否关注
                elif (cmd["action"] == "CheckFocusSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 6:
                                    pairing[key][2] = 7
                                    message1 = json.dumps({"action": "doconfirmfin"})
                                    message2 = json.dumps({
                                        "action": "dopairsecond",
                                        "state": "makeconfirm"})
                                    self.write_message(message1)
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message2)
                                    else:
                                        ServerError(self,"低信誉值用户选择去快手关注对方是否关注时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时不允许去确认对方是否关注")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为6时不是对应会话中的低用户，不能去确认对方是否关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 低信誉值用户选择对方已经关注自己,匹配成功
                elif (cmd["action"] == "ConfirmSuccessSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 7:
                                    pairing[key][2] = 8
                                    # 匹配时就已经创建了state为0的记录
                                    HufenFail123(self,1,"NoErr")
                                    self_int = (self.user.integral)-cost
                                    pair_int = (self.pairuser.integral)-cost
                                    message1 = json.dumps({
                                        "action": "dopairsuccess",
                                        "userid":self.pairuser.userid,
                                        "cost":int(cost),
                                        "integral":self_int})
                                    message2 = json.dumps({
                                        "action": "dopairsuccess",
                                        "userid": self.user.userid,
                                        "cost":int(cost),
                                        "integral":pair_int})
                                    self.write_message(message1)
                                    if self.pairuser in users:
                                        users[self.pairuser].write_message(message2)
                                        User.objects.filter(userid=self.user.userid).update(integral=self_int)
                                        User.objects.filter(userid=self.pairuser.userid).update(integral=pair_int)
                                        # 重置用户状态
                                        self.HufenPos = 0
                                        users[self.pairuser].HufenPos = 0
                                        # 成功互粉后删除会话
                                        del pairing[key]
                                    else:
                                        ServerError(self,"互粉最终确认时 用户:" + self.pairuser.username + "不在用户表中！")
                                else:
                                    ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时不允许确认对方已经关注")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为7时不是对应会话中的低用户，不能去确认对方是否关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")




                #以上是正常流程
                #以下是互粉中断情况
                # 低用户取消/否定去关注匹配用户
                elif (cmd["action"] == "NoConfirmPairFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 0:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_1_1"})
                                            # 互粉终止的记录与通知
                                            TipForError(self,key,message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_1_2"})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时取消去关注发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时取消去关注发送的数据没有state字段")
                                else:
                                    ServerError(self, "会话异常")
                            else:
                                ServerError(self, "DU在会话状态不为0时不允许取消/否定去关注对方")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为0时不是对应会话中的低用户，不能取消/否定去关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 低用户取消/否定已经关注匹配用户
                elif (cmd["action"] == "NoConfirmFocusFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 1:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_2_1"})
                                            # 互粉终止的记录与通知
                                            TipForError(self, key, message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_2_2"})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self,"DU在会话状态为：" + str(pairing[key][2]) + "时取消已经关注发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时取消已经关注发送的数据没有state字段")
                                else:
                                    ServerError(self, "会话异常")
                            else:
                                ServerError(self, "DU在会话状态不为1时不允许取消/否定已经关注对方")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为1时不是对应会话中的低用户，不能取消/否定已经关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 高用户取消去快手确认对方是否关注
                elif (cmd["action"] == "NoCheckFocusFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 2:
                                    message = json.dumps({
                                        "action": "errorpair",
                                        "state": "ErrorGU_0",
                                        "otherid":self.user.userid})
                                    # 互粉终止的记录与通知
                                    TipForError(self, key, message)
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许取消去确认是否被关注")
                            else:
                                ServerError(self, "会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为2时不是对应会话中的高用户，不能取消去确认是否被关注")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 高用户取消/否定对方已经关注自己
                elif (cmd["action"] == "NoConfirmFocusPre") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 3:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_1_1",
                                                "otherid": self.user.userid})
                                            # 互粉终止的记录与通知
                                            TipForError(self, key, message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_1_2",
                                                "otherid": self.user.userid})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时取消/否定对方关注自己发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时取消/否定对方关注自己发送的数据没有state字段")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许取消/否定对方关注自己")
                            else:
                                ServerError(self,"会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为3时不是对应会话中的高用户，不能取消/否定对方关注自己")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")


                # 高用户取消/否定去快手关注对方
                elif (cmd["action"] == "NoConfirmFocusSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 4:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_2_1",
                                                "otherid": self.user.userid})
                                            # 互粉终止的记录与通知
                                            TipForError(self, key, message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_2_2",
                                                "otherid": self.user.userid})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时取消/否定去关注对方发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self,"GU在会话状态为：" + str(pairing[key][2]) + "时取消/否定去关注对方发送的数据没有state字段")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许取消/否定去关注对方")
                            else:
                                ServerError(self,"会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为4时不是对应会话中的高用户，不能取消/否定去关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 高用户取消/否定已经关注对方
                elif (cmd["action"] == "NoConfirmSuccessFirst") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 1:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 5:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_3_1",
                                                "otherid": self.user.userid})
                                            # 互粉终止的记录与通知
                                            TipForError(self, key, message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorGU_3_2",
                                                "otherid": self.user.userid})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self, "GU在会话状态为：" + str(
                                                pairing[key][2]) + "时取消/否定已关注对方发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self,"GU在会话状态为：" + str(pairing[key][2]) + "时取消/否定已关注对方发送的数据没有state字段")
                                else:
                                    ServerError(self, "GU在会话状态为：" + str(pairing[key][2]) + "时不允许取消/否定已关注对方")
                            else:
                                ServerError(self,"会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为5时不是对应会话中的高用户，不能取消/否定已关注对方")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 低用户取消去快手确认对方是否关注
                elif (cmd["action"] == "NoCheckFocusSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 6:
                                    message = json.dumps({
                                        "action": "errorpair",
                                        "state": "ErrorDU_0",
                                        "otherid": self.user.userid})
                                    TipForError(self, key, message)
                                else:
                                    ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时不允许取消去确认对方关注自己")
                            else:
                                ServerError(self,"会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为6时不是对应会话中的低用户，不能取消去确认对方关注自己")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")

                # 低用户取消/否定选择对方已经关注自己
                elif (cmd["action"] == "NoConfirmSuccessSecond") and self.HufenPos == 2:
                    key = get_key(self)
                    if key in pairing:
                        if pairing[key].index(self) == 0:
                            if len(pairing[key]) == 3:
                                if pairing[key][2] == 7:
                                    if "state" in cmd:
                                        if cmd["state"] == "cancel":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_3_1",
                                                "otherid": self.user.userid})
                                            # 互粉终止的记录与通知
                                            TipForError(self, key, message)
                                        elif cmd["state"] == "deny":
                                            message = json.dumps({
                                                "action": "errorpair",
                                                "state": "ErrorDU_3_2",
                                                "otherid": self.user.userid})
                                            TipForError(self, key, message)
                                        else:
                                            ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时取消/否定对方关注自己发送的数据中state字段键值不存在")
                                    else:
                                        ServerError(self,"DU在会话状态为：" + str(pairing[key][2]) + "时取消/否定对方关注自己发送的数据没有state字段")
                                else:
                                    ServerError(self, "DU在会话状态为：" + str(pairing[key][2]) + "时不允许取消/否定对方关注自己")
                            else:
                                ServerError(self,"会话异常")
                        else:
                            ServerError(self, self.user.username + "在会话状态不为7时不是对应会话中的低用户，不能取消/否定对方关注自己")
                    else:
                        ServerError(self, "不存在包含用户：" + self.user.username + "的会话")


                # 确认互粉之前关闭了弹窗
                elif (cmd["action"] == "CancelPairSecond") and self.HufenPos == 2:
                    message = json.dumps({
                        "action": "errorpair",
                        "state": "cancelpair"})
                    key = get_key(self)
                    # 有人点击了确认互粉
                    if key in pairing:
                        # 不处于互粉状态
                        if len(pairing[key]) != 3:
                            self.HufenPos = 0
                            HufenFail045(self, 4, self.user.userid)
                            if self.pairuser in users:
                                users[self.pairuser].HufenPos = 0
                                users[self.pairuser].write_message(message)
                            else:
                                ServerError(self, "用户：" + self.user.username + "不在用户表中")
                        else:
                            ServerError(self, "当前会话状态为：" + str(pairing[key][2]) + "时，确认互粉前关闭弹窗的操作无效")
                    # 没人点击确认互粉
                    else:
                        self.HufenPos = 0
                        HufenFail045(self, 4, self.user.userid)
                        if self.pairuser in users:
                            users[self.pairuser].HufenPos = 0
                            users[self.pairuser].write_message(message)
                        else:
                            ServerError(self, "用户：" + self.user.username + "不在用户表中")

                # 超时
                elif cmd["action"] == "OverTime":
                    if "state" in cmd:
                        # 在互粉过程超时
                        if cmd["state"] == "InHufen":
                            message = json.dumps({
                                "action": "errorpair",
                                "state": "overtime"})
                            HufenFail045(self,0, self.pairuser.userid)
                            # 超时则对方背锅
                            if self.pairuser in users:
                                users[self.pairuser].write_message(message)
                            else:
                                ServerError(self,"超时")
                            key = get_key(self)
                            if key in pairing:
                                del pairing[key]
                        # 在匹配过程超时 服务器原因 此时没有匹配到用户
                        elif cmd["state"] == "InPair":
                            # 退出匹配序列，防止重复提醒
                            if self.user in pairs:
                                self.pairtime = 0
                                del pairs[self.user]
                            else:
                                self.pairtime = 0
                    else:
                        ServerError(self,"json数据中无state字段")
                else:
                    ServerError(self,"异常操作")
            elif "test" in cmd:
                if cmd["test"] == "delete":
                    HufenHistory.objects.all().delete()
                    CancleHf.objects.all().delete()


    def on_close(self):
        if self.user in users:
            del users[self.user]
            print(str(self.user.userid) + "退出互粉大厅")
        if self.user in pairs:
            del pairs[self.user]
            print(str(self.user.userid) + "退出匹配序列")
        key = get_key(self)
        if key in pairing:
            del pairing[key]
            print(str(self.user.userid) + "退出正在匹配序列")
        print("所有用户：")
        for user in users:
            print(user.userid)

class ListHandler(tornado.web.RequestHandler):

    def get(self):
        success = []  # 互粉成功列表
        cancel = []  # 取关列表
        fail = [] #失败列表
        uid = self.get_secure_cookie('uid')
        user = User.objects.filter(userid=int(uid)).first()
        if not user:
            self.render("hufen/list.html", userid=uid)
        else:
            result = HufenHistory.objects.filter(user1=int(uid),state=1)
            for row in result:
                user2 = User.objects.filter(userid=int(row.user2)).first()
                if user2:
                    success.append([user2.userid,user2.username])
                else:
                    success.append([user2.userid, "NoUser"])
            result = HufenHistory.objects.filter(user2=int(uid), state=1)
            for row in result:
                user2 = User.objects.filter(userid=int(row.user1)).first()
                if user2:
                    success.append([user2.userid,user2.username])
                else:
                    success.append([user2.userid, "NoUser"])

            result = CancleHf.objects.filter(userid=int(uid))
            for row in result:
                user2 = User.objects.filter(userid=int(row.cancle_id)).first()
                if user2:
                    cancel.append([user2.userid,user2.username])
                else:
                    cancel.append([user2.userid, "NoUser"])

            result = HufenHistory.objects.filter(user1=int(uid)).exclude(state=1)
            for row in result:
                user2 = User.objects.filter(userid=int(row.user2)).first()
                if user2:
                    fail.append([user2.userid, user2.username])
                else:
                    fail.append([user2.userid, "NoUser"])
            result = HufenHistory.objects.filter(user2=int(uid)).exclude(state=1) #uid=1 state!=1
            for row in result:
                user2 = User.objects.filter(userid=int(row.user1)).first()
                if user2:
                    fail.append([user2.userid, user2.username])
                else:
                    fail.append([user2.userid, "NoUser"])



            self.render("hufen/list.html", userid=user.userid,success=success,cancel=cancel,fail=fail)

class HistoryHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        uid = self.get_secure_cookie('uid')
        print(str(uid) + "进入互粉历史列表")

    def on_message(self, message):
        cmd = json.loads(message);
        uid = self.get_secure_cookie('uid')
        if "action" in cmd:
            # 取消对某用户的关注 举报对方取关
            if cmd["action"] == "CancelFocus":
                if not CancleHf.objects.filter(userid=cmd["otherid"],cancle_id=int(uid)).first():
                    key = str(cmd["otherid"]) + "_" + str(uid)
                    CancleHf.objects.create(CancelId=key,userid=cmd["otherid"],cancle_id=uid)
                if HufenHistory.objects.filter(user1=int(uid), user2=cmd["otherid"]).first():
                    HufenHistory.objects.filter(user1=int(uid), user2=cmd["otherid"]) \
                        .update(state=5, bguser=cmd["otherid"])
                elif HufenHistory.objects.filter(user2=int(uid), user1=cmd["otherid"]).first():
                    HufenHistory.objects.filter(user2=int(uid), user1=cmd["otherid"]) \
                        .update(state=5, bguser=cmd["otherid"])
                message = json.dumps({"action":"tips"})
                self.write_message(message)
                print(str[uid] + "取关了" + str(cmd["otherid"]))
            # 查看自己的关注和粉丝信息

            elif cmd["action"] == "CheckSelf":
                message = json.dumps({
                    "action": "check",
                    "userid":int(uid)})
                self.write_message(message)
                print(str[uid] + "正在进入自己主页查看关注与粉丝情况")


    def on_close(self):
        uid = self.get_secure_cookie('uid')
        print(str(uid) + "退出互粉历史列表")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/hall",HallHandler),
            (r"/hufen",HufenHandler),
            (r"/list",ListHandler),
            (r"/history",HistoryHandler),
        ]
        settings = {
            'cookie_secret':'abc',
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),#当前目录
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),#根目录
            'debug': True
        }
        tornado.web.Application.__init__(self, handlers,**settings)


if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8000)
    thread_pair = HufenPair()
    thread_pair.start()
    # thread_dopair = HufenDoPair()
    # thread_dopair.start()
    tornado.ioloop.IOLoop.instance().start()