from ksht.settings_ import *


DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ksht',
        'USER': 'root',
        'PASSWORD':"root",
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'OPTIONS':{
            "charset": "utf8mb4",
        }
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'/static/').replace('\\','/')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

import redis
redisconn =  redis.Redis(host="127.0.0.1", port=6379)
