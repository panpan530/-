"""
Django settings for shop project.

Generated by 'django-admin startproject' using Django 2.1.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c5qfpkj2g)9n7pl4cv0^1k@n4o3wc@4-e-c#sj8**j1$plt6yz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'buyer',
    'shop',
    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    # 'django-filter',
    'djcelery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'my_middleware.middleware.MyMiddleware',
]


ROOT_URLCONF = 'shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':'shopff',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'USER':'root',
        'PASSWORD':''
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


PRIMARY_KEY = 'hei'


STATIC_URL = '/static/'

STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')]


# 设置文件上传的url路径
MEDIA_URL = '/static/buyer/img/'
# 设置文件上传存储的位置
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

# 富文本编辑器的路径设置
CKEDITOR_UPLOAD_PATH = 'upload' # 相对于'static/media'，在static/media的基础下加入/upload
CKEDITOR_IMAGE_BACKDND = 'pillow'

#  继承用户认证系统需要设置
#去登录的url，用户认证系统的装饰器要用到
LOGIN_URL = '/buyer/login/' #app/方法，就是一个路由
#用户模块
AUTH_USER_MODEL = 'buyer.Buyer'
# 3、验证用户，比如登录,用户验证有时候验证密码不帮我们加密就核对，造成我们登录不成功，
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']

#################配置发送邮件#################
# 1、django中的发邮件的管理类
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# 2、smtp服务器
EMAIL_HOST = 'smtp.qq.com'
# 3、smtp服务器端口号
EMAIL_PORT = 25
# 4、发送邮件的邮箱
EMAIL_HOST_USER = '1154344105@qq.com'
# 5、在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'zsoashjhdtisbafa'
# 6、# 收件人看到的发件人信息
EMAIL_FROM = '天天生鲜<1154344105@qq.com>'



#################支付宝支付#################
APPID = '2016101100663415'


############ celery#########
CELERY_BORKER_URL = 'redis://127.0.0.1:6379/1'


#手机静态文件
STATIC_ROOT = '/opt/shop/static/'

# diango的缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 用户的session信息，历史浏览记录存储在redis数据库9中
        "LOCATION": "redis://127.0.0.1:6379/9",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


#################restful#################
# REST_FRAMEWORK = {
#     # 权限
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
#     ],
#     # 分页
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     # 页码
#     'PAGE_SIZE': 10,
#     # 定制json
#     'DEFAULT_RENDERER_CLASSES': [
#         'buyer.custom.CustomJSONRenderer',
#     ],
#     # 过滤器
#     'DEFAULT_FILTER_BACKENDS': [
#         'django_filters.rest_framework.DjangoFilterBackend',
#     ],
# }


