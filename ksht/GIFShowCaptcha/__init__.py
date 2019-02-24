import random
import logging
import time

from gifshowapi import gifshow
from ksht import settings

__version__ = '0.0.1',


def getgifshow():
    return gifshow().settoken("b9ae59304b5742b4ad13406085fe1f50-264876848")


def photo_comment_list(userid, photoid, pcursor="", count=20):
    while True:
        try:

            return getgifshow().photo_comment_list(userid, photoid, pcursor, count=count)
        except Exception as  e:
            logging.warning((photo_comment_list, e))
            time.sleep(1)


Photos = (
    (50881480, 1424471317,"https://gifshow-10011997.file.myqcloud.com/upic/2016/12/27/18/BMjAxNjEyMjcxODIyMDVfNTA4ODE0ODBfMTQyNDQ3MTMxN18yXzM=.jpg"),
)
#
# def getcode():
#
#     while True:
#         try:
#             for p in Photos:
#                 comments = photo_comment_list(p[0], p[1], count=100)["comments"]
#                 comments.sort(key=lambda obj: obj.get('timestamp'), reverse=False)
#                 for comment in comments:
#                     settings.redisconn.set(
#                         "_django_gifshowcaptcha_key:" + "%s:%s:%s" % (p[0], p[1], comment['author_id']),
#                         comment["content"], ex=24 * 60 * 60)
#             time.sleep(5)
#         except:
#             time.sleep(10)
#
#
# import threading
#
# t = threading.Thread(target=getcode)
# t.setDaemon(True)
# t.start()


class Captcha(object):
    def __init__(self, request):
        self.django_request = request

        self.session_key = '_django_gifshowcaptcha_key'

    def getcode(self):

        try:
            v = self.django_request.session[self.session_key]

            c = False
            for p in Photos:
                if p[1] == v["photo"][1]:
                    c = True
                    break

            if not c:
                raise ValueError()


            return {
                "userid": v['photo'][0],
                "photoid": v["photo"][1],
                "photourl":v["photo"][2],
                "code": v["code"],
            }
        except:
            code = str(random.randint(100000, 999999))
            photo = random.choice(Photos)
            self.django_request.session[self.session_key] = {
                "photo": photo,
                "code": code
            }

            captcha = {
                "userid": photo[0],
                "photoid": photo[1],
                "photourl": photo[2],
                "code": code,
            }
            return captcha

    def validate(self, code):

        if not code:
            return False

        if self.session_key not in self.django_request.session.keys():
            return False

        _codename ="_django_gifshowcaptcha_key:"+ "%s:%s:%s" % (
            self.django_request.session[self.session_key]['photo'][0],
            self.django_request.session[self.session_key]['photo'][1],
            self.django_request.user.userid,
        )
        try:
            code2 = settings.redisconn.get(_codename)
            if not code2:
                return False
            else:
                code2 = code2.decode()

            y1 = code2.lower() == str(code).lower()
            y2 = code2.lower() ==self.django_request.session[self.session_key]['code']
            return y1 and y2
        except:
            return False

    def delcode(self):
        if self.session_key in self.django_request.session.keys():
            del self.django_request.session[self.session_key]


if __name__ == '__main__':
    class c():
        session = {}


    a = c()
    c = Captcha(a)
    # print(c.getcode())
