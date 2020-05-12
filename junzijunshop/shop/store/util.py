from django.shortcuts import render
from hashlib import md5
from store.models import *
from django.utils.decorators import method_decorator

def new_pwd(pwd):
    mi_pwd = md5(pwd.encode('utf-8')).hexdigest()
    return mi_pwd



def wrapper_logined(func):
    def inner(request,*args,**kwargs):
        #如果有session放行
        if request.session.get('logined'):
            return func(request,*args,**kwargs)
        # 问题：当访问 添加店铺时，因为权限被限制，跳转到登陆页面，但登录完没有跳转到添加店铺的页面
        else: #如果没有session跳转到登陆，同时用cookie记住所访问的路径
            response = render(request,'store/login.html')
            full_path = request.get_full_path() #获取没登录时想要跳转页面的路径
            response.set_cookie('full_path',full_path)  #记住路径
            return response
    return inner

def wrapper_store(func):
    def inner(request,*args,**kwargs):
        # 1.获取请求路径
        request_url = request.get_full_path()
      # 2. 获取卖家id
        seller_id = request.session['logined']
        #3.判断这个卖家是否已经注册了店铺
        store = Store.objects.filter(seller_id=seller_id).first()
        #4.判断店铺是否已经存在
        if store:
            #如果店铺已经存在了
            #如果请求的路径是添加店铺
            if request_url == '/store/add_store/':
                return render(request,'store/tip.html',{'tip':'只能有一个店铺'})
            else:
                return func(request,*args,**kwargs)
        #卖家还没有注册店铺，不能添加商品，也不能编辑店铺
        else:
            if request_url == '/store/add_goods/' or request_url == '/store/edit_store/':
                return render(request,'store/tip.html',{'tip':'先添加店铺'})
            # 如果没有店铺但是访问的路径与店铺注册与否无关 ，就让他通过，执行访问的路径
            else:
                return func(request,*args,**kwargs)
    return inner







