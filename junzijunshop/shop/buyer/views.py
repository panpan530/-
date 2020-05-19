from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.views import  View


from buyer.models import *
from django.contrib.auth.decorators import login_required
from shop import settings
from buyer.utils import *
from itsdangerous import SignatureExpired, BadSignature
from django.contrib.auth import authenticate,login,logout
from store.models import *
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Sum
from datetime import datetime
import alipay
import os,datetime
from django.core.cache import cache


#全局变量
#页码显示条数
page_size = 20

def goods_count_incart(request):
    #如果用户登录才能看到购物车，如果没有登录，购物车商品数量显示0
    mycount = 0
    # # 判断是否登录
    if request.user.is_authenticated:
        # 获取当前用户的购物车的数量，如果当前用户下购物车没有商品，返回值的None
        mycount = Cart.objects.filter(buyer=request.user).aggregate(mycount=Sum('count')).get('mycount')
        if mycount == None:
            mycount = 0

    return mycount

#######  注册
class Register(View):
    def get(self,request):
        return render(request,'buyer/register.html')

    def post(self,request):
        # 获取数据
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        cpassword = request.POST.get('cpassword').strip()
        email = request.POST.get('email').strip()
        allow = request.POST.get('allow').strip()
        data = {'cpwd': '密码不一致请重新输入', 'username': username, 'email': email}
        #判断用户名是否存在
        info = Buyer.objects.filter(username=username).first()
        if info:
            username = username + '1'
        # 判断确认密码和密码一不一样
        if password != cpassword:
            return render(request, 'buyer/register.html', locals())
        # 如果全部为空
        if not all([username,password,cpassword,email,allow]):
            return render(request, 'buyer/register.html', {'script':'alert("不能为空")'})
        if len(username)<5 or len(username)>12:
            return render(request, 'buyer/register.html',{'script':'alert("用户名格式错误")'})
        # ********  给数据库赋值 ***********
        # 使用用户认证系统提供的create_user ,方法，密码会直接加密
        buyer = Buyer.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        # 当注册时需要去邮箱激活，刚刚注册还没激活，标记未激活,0为未激活
        buyer.is_active = False
        buyer.save()
        # ************* 邮箱验证 *********************
        #创建要加密的数据：数据是一个字典类型
        data = {'id':buyer.id}
        # 加密
        mi_data = func(data,settings.PRIMARY_KEY,60*60*14)
        # print(request.get_host())#127.0.0.1:8000
        # print(request.scheme) #http
        url = '{}://{}/buyer/active/?data={}'.format(request.scheme,request.get_host(),mi_data)
        #准备发邮件的参数
        #主题
        subject = '天天生鲜注册认证信息'
        from_email = settings.EMAIL_FROM  #设置发件人
        recipient_list = [buyer.email] #收件人，注册的用户email
        message = ''
        html_message = '<h1>%s欢迎您注册天天生鲜<h1>，<a href="%s">点击去激活</a>'%(buyer.username,url)
        # 发送
        from my_celery.tasks import send_email_celery
        send_email_celery.delay(subject,message,from_email,recipient_list,html_message=html_message)
        return HttpResponse('注册、成功')
    ####### 去qq设置开启

#######  激活
class Active(View):
    def get(self,request):
        #获取数据
        data = request.GET.get('data')
        try:
            en_mi = en_func(data,settings.PRIMARY_KEY,60*60*14)
        except SignatureExpired:
            return HttpResponse('认证消息已经过期')
        except BadSignature:
            return HttpResponse('操作有误')
        else:
            buyer = Buyer.objects.filter(id=en_mi.get('id')).first()
            buyer.is_active = True
            buyer.save()
            return HttpResponse("hello,激活成功")


  #### 登录

        # 登录

class Login(View):
    def get(self, request):
        # 判断上次是否存在cookie
        remember = request.COOKIES.get('username')
        if not remember:
            remember = ''
        info = {'remember':remember}
        return render(request,'buyer/login.html',info)

    def post(self,request):
        #获取用户名密码
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()
        #判断用户名密码是否存在，密码是否正确
        # data_username = Buyer.objects.filter(username=username).first()
        # if not data_username:
        #     return render(request, 'buyer/login.html', {'msg1': '用户名不存在'})
        # 用户认证系统的功能，自动与加密了的密码进行核对,还有判断是否有本来想要走的路径
        data = authenticate(username=username,password=password)
        if data : #如果已经激活
            if data.is_active:#如果账号密码无误记住用户的登录状态
                # 用户认证系统：记录用户的登录状态
                login(request, data)
                #判断是否有要跳转的url
                next_url = request.GET.get('next')
                if next_url:
                    response = redirect(next_url)
                else:
                    response = redirect('/buyer/index/')
                # 判断用户是否记住用户名，如果记住用户名创建cookie
                remember = request.POST.get('remember')
                if remember:
                    response.set_cookie('username',username)
                    return response
                #如果没有session的值，删除可能之前已经创建的cookie
                else:
                    response.delete_cookie('username')
                    return response
            else:# 没有被激活
                return HttpResponse('<a href="/buyer/register/">没有被激活，重新注册去邮箱激活</a>')
        else:
            if not  data : # 如果有用户名没有data说明密码错误
                return render(request, 'buyer/login.html', {'msg': '密码不正确','u_name':username})

#### 首页
class Index(View):
    def get(self,request):
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        #从数据库获取数据
        dic = {'cart_goods_cart':cart_goods_cart}
        #猜你喜欢类型，根据buyer的id找views和start_time 排序之后根据goods_id,在找对应的goodstype,再找到同类型的商品
        #'-start_time' 降序
        buyer_id = request.user.id

        ############  时间最新的商品  ##########

        goodsrelave = GoodsRelave.objects.filter(buyer_id = buyer_id).order_by('-start_time')[:4]
        #取到goods的id
        goodst_id_lst = []
        for goods_id in goodsrelave:
            goodst_id_lst.append(goods_id.goods_id)
        #在找对应的goodstype
        goodstypet_id_lst = []
        goods = Goods.objects.filter(pk__in=goodst_id_lst)
        for goodstype_id in goods:
            goodstypet_id_lst.append(goodstype_id.goodstype_id)
        goods_time_news = Goods.objects.filter(goodstype_id__in=goodstypet_id_lst).order_by('-sales')[:10]

        ############  点击量最多的商品  ##########

        goodsrelave = GoodsRelave.objects.filter(buyer_id=buyer_id).order_by('-views')[:5]
        # 取到goods的id
        goodsv_id_lst = []
        for goods_id in goodsrelave:
            goodsv_id_lst.append(goods_id.goods_id)
        # 在找对应的goodstype
        goodstypev_id_lst = []
        goods = Goods.objects.filter(pk__in=goodsv_id_lst)
        for goodstype_id in goods:
            goodstypev_id_lst.append(goodstype_id.goodstype_id)
        goods_views_news = Goods.objects.filter(goodstype_id__in=goodstypev_id_lst).order_by('-create_time')[:10]
        #去重
        st = set()
        for goods_views in goods_views_news:
            st.add(goods_views.id)
            if len(st) == 4 :
                break
        for goods_views in goods_views_news:
            st.add(goods_views.id)
            if len(st) == 8 :
                break
        goods_id_grep = list(st)
        #根据去重之后的去取商品
        goods_views_news = Goods.objects.filter(pk__in=goods_id_grep[:4]).order_by('-create_time')
        goods_time_news = Goods.objects.filter(pk__in=goods_id_grep[4:8]).order_by('-sales')

        # 1.商品的类型，图片
        goodstype = GoodsType.objects.filter(id__in=[1,2,3,4,5,6])
        for goodtype in goodstype:
        # 2.此类型中价格中等的水果图片名称价格,必须是没有被删除，和已经上架,库存>0
        #价格最大的前四个 ， 库存大于10才加入前端显示
            goodtype.three = Goods.objects.filter(goodstype_id=goodtype.id, is_delete=False, up=True,number__gt=10).order_by('-price')[:4]
            # 3.此类型中销量最好的三种商品名称
            goodtype.four = Goods.objects.filter(goodstype_id=goodtype.id, is_delete=False, up=True,number__gt=10).order_by('sales')[:3]
           # 必须要用点goodtype.four，的方式添加，类似于临时给添加字段赋值，能记住从1开始的所以值
        return render(request,'buyer/index.html',locals())


class Detail(View):# 商品详情
    def get(self,request):
        id = request.GET.get('goods_id')
        # 如果用户没有登录就设置为0
        buyer_id = request.user.id
        if not buyer_id:
            buyer_id = request.get_host()
        #判断有没有缓存：
        good_cache = cache.get(id)
        if good_cache:
            good = good_cache
        else:
            #获取到这个商品的所以字段信息
            good = Goods.objects.filter(id=id).first()
            #之后做缓存:商品的id作为键，商品信息为值
            cache.set(id, good, 60 * 60 * 14)
        # 获取这个商品所属的类型
        goodstype = GoodsType.objects.filter(id=good.goodstype_id).first()
        #必须要是上架，并且没有被删除的
        goods_left = Goods.objects.filter(is_delete=False, up=True,goodstype=good.goodstype).order_by('sales')[:2]
        # 让商品的浏览量加1,同时添加访问时间
        goodsrleave = GoodsRelave.objects.filter(goods_id=good.id).first()

        #如果表中还没有对应的goods_id那就先添加
        if not goodsrleave:
            GoodsRelave.objects.create(
                goods_id = good.id,
                buyer_id = request.user.id,
                views =  1,
                start_time = datetime.datetime.now()
            )
        else:
            goodsrleave.views = goodsrleave.views + 1
            # 如果已经有了end_time就不再添加start_time
            if not goodsrleave.end_time:
                goodsrleave.start_time = datetime.datetime.now()
                goodsrleave.save()
        return render(request,'buyer/detail.html',locals())

# 个人信息
class User_center_info(View):
    @method_decorator(login_required)
    def get(self,request):
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'cart_goods_cart': cart_goods_cart}
        #通过用户验证系统得到买家的id
        buyer_id = request.user.id
        buyer_info = Address.objects.filter(buyer_id=buyer_id).first()
        return render(request,'buyer/user_center_info.html',locals())

#全部订单
class User_center_order(View):
    @method_decorator(login_required)
    def get(self,request):
        page_now = request.GET.get('page_now')
        if not page_now:
            page_now = 1
        page_now = int(page_now)
        #获取订单表中的所有订单组合，一个订单又有多件商品
        order_list = Order.objects.filter(buyer=request.user)
        #分页
        pagesize = 3
        my_paginator = Paginator(order_list,pagesize)
        # 求总页码
        sum_page = my_paginator.num_pages
        # 当前页对象，如果我们把最后一页删除了会导致找不到页码报错
        try:  # 如果报错
            my_page = my_paginator.page(page_now)
        except:  # 如果不是第一页就跳到下一页，如果是第一页就正常往下走
            # 如果get输入访问，page>总页数让page = 最后一页
            if page_now > sum_page:
                page_now = sum_page
                return redirect('/store/user_center_order/?page={}'.format(page_now))
            if page_now < 1:
                return redirect('/store/user_center_order/?page={}'.format(1))
        # 设置显示出的页数
        num = 2  # 实际显示出num * 2 + 1 个页码
        # 当前页减num 是 如果请求的当前页是5，那么前面会显示5-num 个页码
        start = page_now - num
        if start <= 0:
            start = 1
        # 当前页减num 是 如果请求的当前页是5，那么后面会显示5+num 个页码，加上当前页总共就显示出11个页码
        end = page_now + num
        # 实际显示出num * 2 + 1 个页码 ,所以结尾加开头必须保持一致，前num个开头结尾是不相等的，当不相等事给end重新赋值
        if end - start != num * 2 + 1:
            end = start + num * 2
        # 获取所有页数
        page_range = my_paginator.page_range[start - 1:end]  # 显示出的页码是奇数
        # page_range = my_paginator.page_range[start - 1:end - 1] #显示出的页码是偶数
        # 获取当前页的数据内容
        order_list = my_page.object_list
        # 获取数据的总个数
        count = my_paginator.count
        data = {
            'order_list': order_list,
            'page_now': page_now,
            'my_page': my_page,
            'page_range': page_range,
            'page_size': page_size,
            'count': count,
            'sum_page': sum_page,
        }
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'goods_cart': cart_goods_cart}
        return render(request, 'buyer/user_center_order.html', locals())

#收货地址
class User_center_site(View):
    @method_decorator(login_required)
    def get(self,request):
        buyer_id = request.user.id
        #获取此买家所有的地址
        addrs = Address.objects.filter(buyer_id=buyer_id)
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'cart_goods_cart': cart_goods_cart,'addrs':addrs}
        return render(request,'buyer/user_center_site.html',locals())

    @method_decorator(login_required)
    def post(self,request):
        name = request.POST.get('username')
        addr = request.POST.get('addr')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        addr = Address.objects.create(
            name = name,
            addr = addr,
            password = password,
            phone = phone,
            buyer_id = request.user.id,
        )

        return redirect('/buyer/user_center_site/')

##页面搜索
class List(View):
    def get(self,request):
        page_now = request.GET.get('page')
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        if not page_now:
            page_now = 1
        page_now = int(page_now)
        # 获取请求的关键词
        if not keyword:
            keyword = ''
        if not sort:
            sort = 1
        sort = int(sort)
        # 从数据库获取数据，模糊查询，只要包含关键词的，#is_delete=False 并且没有被删除的
        if sort == 3:
            qs_goods = Goods.objects.filter(name__icontains=keyword,up=True,is_delete=False).order_by('sales')
        if sort == 2:
            qs_goods = Goods.objects.filter(name__icontains=keyword,up=True,is_delete=False).order_by('price')
        else:
            qs_goods = Goods.objects.filter(name__icontains=keyword,up=True,is_delete=False).order_by('-id')
        # 页面左边的推荐商品数据
        goods_left = Goods.objects.filter(is_delete=False, up=True).order_by('-id')[:2]
        my_paginator = Paginator(qs_goods, page_size)
        # 求总页码
        sum_page = my_paginator.num_pages
        # 当前页对象，如果我们把最后一页删除了会导致找不到页码报错
        try:  # 如果报错
            my_page = my_paginator.page(page_now)
        except:  # 如果不是第一页就跳到下一页，如果是第一页就正常往下走
            # 如果get输入访问，page>总页数让page = 最后一页
            if page_now > sum_page:
                page_now = sum_page
                return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now, keyword))
            if page_now < 1:
                return redirect('/store/list_goods/?page={}&keyword={}'.format(1, keyword))
        # 设置显示出的页数
        num = 2 # 实际显示出num * 2 + 1 个页码
        # 当前页减num 是 如果请求的当前页是5，那么前面会显示5-num 个页码
        start = page_now - num
        if start <= 0:
            start = 1
        # 当前页减num 是 如果请求的当前页是5，那么后面会显示5+num 个页码，加上当前页总共就显示出11个页码
        end = page_now + num
        # 实际显示出num * 2 + 1 个页码 ,所以结尾加开头必须保持一致，前num个开头结尾是不相等的，当不相等事给end重新赋值
        if end - start != num * 2 + 1:
            end = start + num * 2
        # 获取所有页数
        page_range = my_paginator.page_range[start - 1:end]  # 显示出的页码是奇数
        # page_range = my_paginator.page_range[start - 1:end - 1] #显示出的页码是偶数
        # 获取当前页的数据内容
        list_goods = my_page.object_list
        # 获取数据的总个数
        count = my_paginator.count
        data = {
            'list_goods': list_goods,
            'keyword': keyword,
            'page_now': page_now,
            'my_page': my_page,
            'page_range': page_range,
            'page_size': page_size,
            'count': count,
            'sum_page': sum_page,
            'goods_left': goods_left,
            'sort':sort,
        }
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'goods_cart': cart_goods_cart}
        return render(request, 'buyer/list.html', locals())

#    #####  查看更多
class Readmore(View):
    def get(self,request):
        page_now = request.GET.get('page')
        keyword = request.GET.get('keyword')
        sort = request.GET.get('sort')
        if not page_now:
            page_now = 1
        page_now = int(page_now)
        # 获取请求的关键词
        if not keyword:
            keyword = ''
        if not sort:
            sort = 1
        sort = int(sort)
        # 从数据库获取数据，模糊查询，只要包含关键词的，#is_delete=False 并且没有被删除的
        if sort == 3:
            qs_goods = Goods.objects.filter(name__icontains=keyword, up=True, is_delete=False).order_by('sales')
        if sort == 2:
            qs_goods = Goods.objects.filter(name__icontains=keyword, up=True, is_delete=False).order_by('price')
        else:
            qs_goods = Goods.objects.filter(name__icontains=keyword, up=True, is_delete=False).order_by('-id')
        ############查看更多 开始 ########
        # 查看更多 的 页面数据，如果点击的是查看更多，url会传入商品类型id，如果获取到商品类型的id说明用户点击的是查看更多
        goodtype_id = request.GET.get('goodtype')
        if not goodtype_id:
            goodtype_id = 1
        goodtype = GoodsType.objects.filter(id=goodtype_id).first()
        qs_goods = Goods.objects.filter(name__icontains=keyword,goodstype_id=goodtype_id,up=True,is_delete=False).order_by('sales')
        goods_left = Goods.objects.filter(is_delete=False, up=True,goodstype_id=goodtype_id).order_by('-id')[:2]
        my_paginator = Paginator(qs_goods, page_size)
        # 求总页码
        sum_page = my_paginator.num_pages
        # 当前页对象，如果我们把最后一页删除了会导致找不到页码报错
        try:  # 如果报错
            my_page = my_paginator.page(page_now)
        except:  # 如果不是第一页就跳到下一页，如果是第一页就正常往下走
            # 如果get输入访问，page>总页数让page = 最后一页
            if page_now > sum_page:
                page_now = sum_page
                return redirect('/store/readmore/?page={}&keyword={}'.format(page_now, keyword))
            if page_now < 1:
                return redirect('/store/readmore/?page={}&keyword={}'.format(1, keyword))
        # 设置显示出的页数
        num = 2  # 实际显示出num * 2 + 1 个页码
        # 当前页减num 是 如果请求的当前页是5，那么前面会显示5-num 个页码
        start = page_now - num
        if start <= 0:
            start = 1
        # 当前页减num 是 如果请求的当前页是5，那么后面会显示5+num 个页码，加上当前页总共就显示出11个页码
        end = page_now + num
        # 实际显示出num * 2 + 1 个页码 ,所以结尾加开头必须保持一致，前num个开头结尾是不相等的，当不相等事给end重新赋值
        if end - start != num * 2 + 1:
            end = start + num * 2
        # 获取所有页数
        page_range = my_paginator.page_range[start - 1:end]  # 显示出的页码是奇数
        # page_range = my_paginator.page_range[start - 1:end - 1] #显示出的页码是偶数
        # 获取当前页的数据内容
        list_goods = my_page.object_list
        # 获取数据的总个数
        count = my_paginator.count
        data = {
            'list_goods': list_goods,
            'keyword': keyword,
            'page_now': page_now,
            'my_page': my_page,
            'page_range': page_range,
            'page_size': page_size,
            'count': count,
            'sum_page': sum_page,
            'goods_left': goods_left,
            'sort': sort,
            'goodtype': goodtype,
        }
        ###  获取的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'goods_cart': cart_goods_cart}
        return render(request, 'buyer/readmore.html', locals())

        ############查看更多 结束########

# 在详情添加到购物车
class Add_cart(View):
    @method_decorator(login_required)
    def post(self,request):
        #获取ajax发来的参数
        good_id = request.POST.get('goods_id')
        #获取加入购物车的数量
        count = request.POST.get('count')
        buyer = request.user
        #判断数据库是否存在该用户添加的同种商品，如果有了只加数量
        cart = Cart.objects.filter(buyer_id=buyer.id,goods_id=good_id).first()
        if cart:
            cart.count += int(count)
            cart.save()
            # 如果数据库没有加入数据库
        else:
            Cart.objects.create(
                buyer = buyer,
                count = count,
                goods_id = good_id,
            )
        # 把数据回显给ajax，让页面显示购物车商品数量
        data = {
            'goods_count':goods_count_incart(request),
        }
        return JsonResponse(data)

# 购物车
class CartList(View):
    @method_decorator(login_required)
    def get(self,request):
        ###  获取购物车的商品数量
        cart_goods_cart = goods_count_incart(request)
        # 从数据库获取数据
        dic = {'goods_cart': cart_goods_cart}
        #从数据库获取购物车数据
        goods_incart = Cart.objects.filter(buyer=request.user)
        sum_price = 0 #所有商品总价格
        sum_count = 0 #购物车商品的总数量
        for goods_cart in goods_incart:
            sum_price += goods_cart.goods.price * goods_cart.count
            sum_count += goods_cart.count
        data = {
            'sum_price':sum_price,
            'sum_count':sum_count,
            'goods_incart':goods_incart,

        }

        return render(request,'buyer/cart.html',locals())

#删除购物车中的商品
class Cart_delete(View):
    @method_decorator(login_required)
    def post(self,request):
        cart_id = request.POST.get('cart_id')
        goods_cart = Cart.objects.filter(id=cart_id).first()
        goods_cart.delete()
        cart_count = goods_count_incart(request)
        data = {
            'count':cart_count,
        }
        return JsonResponse(data)


# 当我们直接在购物车更改商品数量时，要更新数据库的商品数量
class  Cart_Update(View):
    @method_decorator(login_required)
    def post(self,request):
        cart_id = request.POST.get('cart_id')
        count = request.POST.get('count')
        cart = Cart.objects.filter(id=cart_id).first()
        # 把数据库的商品数量更新
        cart.count = count
        cart.save()
#         获取购物车所有商品的总数
        total_count = goods_count_incart(request)
        # 把总数传给ajax刷新页面
        data = {
            'total_count':total_count,
        }
        return JsonResponse(data)

# 结算
class Place_Order(View):
    @method_decorator(login_required)
    def post(self,request):
        # 获取被选中的商品的id
        cart_ids = request.POST.getlist('cart_ids')
        #获取数据库的数据
        cart_goods_list = Cart.objects.filter(id__in=cart_ids)
        if not cart_goods_list:
            return render(request,'buyer/cart.html')
        #算出所有商品数量和总价格
        sum_count = 0
        sum_price = 0
        for cart_goods in cart_goods_list:
            sum_count += cart_goods.count
            sum_price += cart_goods.goods.price * cart_goods.count
        yunfei = 10
        #获取此用户的默认的地址
        address = Address.objects.filter(buyer=request.user,isdefault=1).first()
        data = {
            'cart_goods_list':cart_goods_list,
            'sum_count':sum_count,
            'sum_price':sum_price,
            'yunfei':yunfei,
            'address':address,
            'cart_ids':'-'.join(cart_ids), # 把所有在提交订单的商品id 拼接作为一个保存
        }
        return render(request,'buyer/place_order.html',data)

## 点击结算，数据返回给ajax，在前端进行跳转
class Order_Submit(View):
    @method_decorator(login_required)
    def post(self,request):
        #获取到的是之前拼接的所有id
        cart_ids = request.POST.get('cart_ids')
        address_id = request.POST.get('address_id')
        paymethod = request.POST.get('paymethod')
        cart_ids = cart_ids.split('-')
        yunfei = 10
        # 算出所有商品数量和总价格
        sum_count = 0
        sum_price = 0
        # 获取数据 提交订单的所有商品列表
        order_list = Cart.objects.filter(id__in=cart_ids)
        if order_list:
            #oder 是 订单中的某个商品，但是是保存在订单表中的
            for cart in order_list:
                #判断库存，如果库存不足
                if cart.count > cart.goods.number:
                    return JsonResponse({'error':1})
                else:
                    #如果库存充足，减少库存
                    cart.goods.number -= cart.count
                    sum_count += cart.count
                    sum_price += cart.goods.price * cart.count
            # 把订单添加到数据库中
            order = Order.objects.create(
                #把id 设置为用户的id加订单创建的时间
                id = str(request.user.id) + datetime.today().strftime('%Y%m%d%H%M%S'),
                buyer = request.user,
                address_id = address_id,
                paymethod = paymethod,
                totalcount = sum_count,
                totalprice = sum_price,
                freight = yunfei,
            )
            # 把订单添加到数据库中的订单明细，记录订单的初始状态
            for cart in order_list:
                OrderDetail.objects.create(
                    order = order,
                    goods = cart.goods,
                    count = cart.count,
                    price = cart.goods.price,
                    name = cart.goods.name,
                    image = cart.goods.image,
                    unite = cart.goods.unite,
                )
                #下单后，把购物车的下单商品删除
            for cart in order_list:
                cart.delete()
            return JsonResponse({'error': 0})
        else:
            return  redirect('/buyer/index/')

# 实现支付
class Order_Pay(View):
    def post(self,request):
        # 获取参数
        order_id = request.POST.get('order_id')
        #找到对应的订单
        order = Order.objects.filter(id=order_id,status=1,buyer=request.user,paymethod=3).first()
         #判断
        if not order:
            return HttpResponse({'res':1,'msg':'订单错误'})
        #初始化：私钥和公钥的路径，读写
        app_private_key_string = open(os.path.join(settings.BASE_DIR,r'buyer/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR,r'buyer/app_public_key.pem')).read()
        #创建sdk对象
        alipay = AliPay(
            appid=settings.APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug = True  # 默认False
        )
        #调用支付接口
        subject = '天天生鲜订单{}'.format(order.id)
        #总价钱
        total_pay = order.totalprice + order.freight
        #把相应的数据付给支付宝，到时候会显示在url中
        # 电脑网站需要跳转到https://openapi.alipay.com/gateway.do? + order_string进行支付
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order.id,
            total_amount=str(total_pay),
            subject=subject,
            return_url="http://127.0.0.1:8000/buyer/pay_result/",
            notify_url="http://127.0.0.1:8000/buyer/pay_result/",  # 可选, 不填则使用默认notify url
        )
        # 跳转到支付路径：
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        #把数据返回给ajax
        return JsonResponse({'res':2,'msg':'成功','pay_url':pay_url})



#获取支付结果
class Pay_Result(View):
    def get(self,request):
        #获取订单id,订单号，下单后产生的
        out_trade_no = request.GET.get('out_trade_no')
        #获取订单交易号，付款后产生的
        trade_no = request.GET.get('trade_no')
        #获取交易金额
        total_amount = request.GET.get('total_amount')
        #获取交易时间
        timestamp = request.GET.get('timestamp')
        #与支付宝创建连接，把我们的信息发送给支付宝
        app_private_key_string = open(os.path.join(settings.BASE_DIR, r'buyer/app_private_key.pem')).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, r'buyer/app_public_key.pem')).read()
        # 创建sdk对象
        alipay = AliPay(
            appid=settings.APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        # #获取交易结果，如果交易成功
        result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status","") == "TRADE_SUCCESS":
            flag = True
        else:
            flag = False
        #修改数据库中的订单状态out_trade_no是订单id,trade_no是订单交易号
        if flag:#如果付款成功，改变数据库的支付状态
            order = Order.objects.filter(id=out_trade_no).first()
            order.status = 2
            order.paynumber = trade_no
            order.save()
        data = {
            'out_trade_no':out_trade_no,
            'total_amount':total_amount,
            'trade_no':trade_no,
            'timestamp':timestamp,
            'flag':flag,
        }
        return render(request,'buyer/pay_result.html',data)




class Table(View):
    def get(self,request):
        return  render(request, 'buyer/tb.html')



from buyer.filterset import *
from rest_framework import  viewsets
from buyer.my_serializers import  *
from rest_framework.decorators import action
from rest_framework.response import Response

hotkwlist = []                 #热搜关键字定义为全局变量不会呗清空
hotkwtime =  10                #热搜关键字缓存时间
buyerhistorykwtime = 604800    #买家的搜索历史缓存时间
searchkwtimes = 3              #搜索几次以后就被取为热搜


#  缓存卖家搜索历史
def rediscacheofkw(request,kw):
    buyerid = request.query_params.get('wxbuyerid')
    print(buyerid,"@@@@@@@@@@@@@@@@@@@@@@")
    if buyerid=="undefined" or kw == "None" or kw == "None":
        return
    # 记一下全部的kw用来做热搜
    hotkwlist.append(kw)
    cache.set("hotkw4", hotkwlist, hotkwtime)
    # 以列表的形式缓存，键是buyerID,列表中存kw,存的时候判断是否已经存在
    kwlistofbuyer = cache.get(buyerid)
    # 判断，如果有缓存，使用，如果没有缓存，查询然后缓存，再使用
    if kwlistofbuyer:
        print('添加历史搜索之前', kwlistofbuyer)
        if len(kwlistofbuyer) > 10:
            del kwlistofbuyer[0]
        if kw not  in kwlistofbuyer:
            kwlistofbuyer.append(kw)
        cache.set(buyerid, kwlistofbuyer, buyerhistorykwtime)
        print('添加之后', kwlistofbuyer)
    else:
        listkW = [kw]
        print('新卖家缓存', listkW)
        cache.set(buyerid, listkW, buyerhistorykwtime)

######## 获取全部的访问接口是 /buyer/history_api
class GoodsViewSet(viewsets.ModelViewSet):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer

    # 访问接口是/buyer/history_api/findgoods?id=3     id是类型id
    @action(detail=False,methods=['get'])
    def findgoods(self,request):
        # get请求是query_params,post是data
        Goods_id = request.query_params.get('id')
        if Goods_id == "0":
            rs = Goods.objects.all().order_by('-sales')
        else:
            rs = Goods.objects.filter(goodstype_id=Goods_id)
        rss = GoodsSerializer(instance=rs,many=True)
        return Response(rss.data)

    # 访问接口是/buyer/history_api/goodsdetail?id=3     id是商品id
    @action(detail=False, methods=['get'])
    def goodsdetail(self,request):
        # get请求是query_params,post是data
        Goods_id = request.query_params.get('id')
        rs = Goods.objects.filter(id=Goods_id)
        rss = GoodsSerializer(instance=rs,many=True)
        return Response(rss.data)

        # 访问接口是/buyer/history_api/tjgoodstype?typeid=3     推荐类目
    @action(detail=False, methods=['get'])
    def tjgoodstype(self, request):
        # get请求是query_params,post是data
        typeid = request.query_params.get('typeid')
        if typeid == "0":  # 猜你喜欢 -是降序
            rs = Goods.objects.order_by('-sales')[:88]
            rss = GoodsSerializer(instance=rs, many=True)
            return Response(rss.data)
        if typeid == "1":  # 便宜好货
            rs = Goods.objects.filter(price__lt=200).order_by('-sales')[:88]
            rss = GoodsSerializer(instance=rs, many=True)
            return Response(rss.data)
        if typeid == "2":  # 聚划算
            rs = Goods.objects.order_by('price')[:88]
            rss = GoodsSerializer(instance=rs, many=True)
            return Response(rss.data)
        if typeid == "3":  # 买家秀
            rs = Goods.objects.order_by('sales')[:88]
            rss = GoodsSerializer(instance=rs, many=True)
            return Response(rss.data)

    # 访问接口是/buyer/history_api/saleshot
    @action(detail=False, methods=['get'])
    def saleshot(self, request):
        rs = Goods.objects.order_by('sales')[:1]
        rss = GoodsSerializer(instance=rs, many=True)
        return Response(rss.data)
#    访问接口是/buyer/history_api/newgood
    @action(detail=False, methods=['get'])
    def newgood(self, request):
        rs = Goods.objects.order_by('-id')[:1]
        rss = GoodsSerializer(instance=rs, many=True)
        return Response(rss.data)

    # 访问接口是/buyer/history_api/GoodsByKeyWord/?typeid=2&kw=2&wxbuyerid=    类目类别和关键字搜索商品
    @action(detail=False, methods=['get'])
    def GoodsByKeyWord(self, request):
        # get请求是query_params,post是data
        kw = request.query_params.get('kw')
        typeid = request.query_params.get('typeid')
        # wxbuyerid = request.query_params.get('wxbuyerid')
        # 缓存关键字，先判断该关键字有没有缓存的商品，有的话直接使用，同时需要把关键字缓存到对应的用户id里
        rs = Goods.objects.filter(name__icontains=kw,up=True,is_delete=False,goodstype_id=typeid).order_by('sales')
        if typeid == "0": # 全部的类别
            rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False).order_by(
                'sales')
        rss = GoodsSerializer(instance=rs, many=True)
        return Response(rss.data)

        # 访问接口是/buyer/history_api/GoodsByKeyWord_Home/?kw=2&wxbuyerid=    主页的关键字搜索商品，缓存之后返回数据
    @action(detail=False, methods=['get'])
    def GoodsByKeyWord_Home(self, request):
        # get请求是query_params,post是data
        kw = request.query_params.get('kw')
        rediscacheofkw(request, kw)
        # 缓存关键字，先判断该关键字有没有缓存的商品，有的话直接使用，同时需要把关键字缓存到对应的用户id里
        rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False).order_by(
            'sales')
        rss = GoodsSerializer(instance=rs, many=True)
        return Response(rss.data)

        # 访问接口是/buyer/history_api/KeyWordofbuyerid/?wxbuyerid=    点击首页输入款促发返回搜索历史
    @action(detail=False, methods=['get'])
    def KeyWordofbuyerid(self, request):
        # get请求是query_params,post是data
        wxbuyerid = request.query_params.get('wxbuyerid')
        kwlist = cache.get(wxbuyerid)
        return Response(kwlist)

    # 访问接口是/buyer/history_api/gethotkw    点击首页输入款促发返回热搜关键词
    @action(detail=False, methods=['get'])
    def gethotkw(self, request):
        rekwls = []
        dic = {}
        lskw = []
        if not cache.get("sorthotkw12" ):
            hotkwlist = cache.get("hotkw4")
            if hotkwlist:
                for kw in hotkwlist:
                    if kw in rekwls:
                        dic[kw] = dic[kw] + 1
                    else:
                        dic[kw] = 1
                        rekwls.append(kw)
            for k,v in dic.items():
                if v > searchkwtimes:
                    lskw.append(k)
            cache.set("sorthotkw12", lskw, hotkwtime)
        print('add')
        sorthotkw = cache.get("sorthotkw12")
        return Response(sorthotkw)

        # 访问接口是/buyer/history_api/GoodsByKeyWordAndLimit/?Limitid=2&kw=2    关键字和条件搜索商品   "33_q5BXSDRHnvRhQc_mIIaHwKzBk9hna-IxgvPk4ROKdWmdxhYsrSu2bu9DF64"
    @action(detail=False, methods=['get'])
    def GoodsByKeyWordAndLimit(self, request):
        # get请求是query_params,post是data
        kw = request.query_params.get('kw')
        Limitid = request.query_params.get('Limitid')
        rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False)
        if Limitid == "1":
            rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False).order_by('sales')
        elif Limitid == "2":
            rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False).order_by('-price')
        elif Limitid == "3":
            rs = Goods.objects.filter(name__icontains=kw, up=True, is_delete=False).order_by('price')
        rss = GoodsSerializer(instance=rs, many=True)
        return Response(rss.data)



class EchartsViewSet(viewsets.ModelViewSet):
    queryset = GoodsRelave.objects.all()
    serializer_class = EchartsSerializer



# 类别
class GoodsTypeViewSet(viewsets.ModelViewSet):
    queryset = GoodsType.objects.all()
    serializer_class = GoodsTypeSerializer






