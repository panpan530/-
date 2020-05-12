from celery import Celery
from shop import settings
from django.core.mail import send_mail

# 调用django的环境
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop.settings')
import django
django.setup()

# 创建celery对象redis://127.0.0.1:6379/1
my_celery = Celery('my_celery.tasks',broker=settings.CELERY_BORKER_URL)

@my_celery.task
def send_email_celery(subject, message, from_email, recipient_list, html_message=None):
    print('开始发送')
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
    print('结束')








