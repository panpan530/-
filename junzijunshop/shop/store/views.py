from django.shortcuts import render, redirect
from django.views import View
from store.models import *
from django.http import HttpResponse, JsonResponse
from hashlib import md5
import uuid, os
from shop import settings
from store.util import *
from shop.settings import *
from django.core.paginator import Paginator
from buyer.models import *

# 规定显示数据条数/每页
page_size = 6

class MyDecoratorMixinLogin(object):
    @classmethod
    def as_view(cls,*args,**kwargs):
        view = super().as_view(*args,**kwargs)
        view = wrapper_logined(view)
        return view


class MyDecoratorMixinStore(object):
    @classmethod
    def as_view(cls,*args,**kwargs):
        view = super().as_view(*args,**kwargs)
        view = wrapper_store(view)
        return view


class Register(View):
    def get(self, request):
        return render(request, 'store/register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        dic = {}
        user = Seller.objects.filter(username=username).first()
        if not user:
            Seller.objects.create(
                username=username,
                password=new_pwd(password),
            )
            return HttpResponse('恭喜您，注册成功去登录')
        else:
            dic1 = {'username': username}
            dic['haved_name'] = '用户名已被占用'
            return render(request, 'store/register.html', locals())


class Login(View):
    def get(self, request):
        cookie_user = request.COOKIES.get('cookie_user')
        # 判断进入的客户cookie存不存在，存在的话显示cookie内容，不存在的显示‘’，而不是none;
        if not cookie_user:
            cookie_user = ''
        return render(request, 'store/login.html', locals())

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        choice_remember = request.POST.get('choice_remember')
        dic = {}
        seller = Seller.objects.filter(username=username,password=new_pwd(password)).first()
        # 如果用户名正确密码错误提交的时候显示
        if seller == None:
            dic['error_pwd'] = '错误或用户名不正确'
            dic['bk_name'] = username
            return render(request, 'store/login.html', locals())
        #登录成功
        else:
            response = render(request, 'store/qiut.html')
            # 获取登录前要访问的路径
            full_path = request.COOKIES.get('full_path')
            # 创建sesion
            request.session['logined'] = seller.id
            if full_path: #如果是想访问其他网站
                response = redirect(full_path)
                response.delete_cookie('full_path')
            if choice_remember:#如果选记住用户名就创建cookie
                response.set_cookie('cookie_user', username,60*60*14)
                return response
            else:  # 如果没有选择记住用户名，删除cookie
                response.delete_cookie('cookie_user')
                return response


def check_name(request):
    dic = {}
    name = request.GET.get('name')  # 失去焦点后获取
    if Seller.objects.filter(username=name).exists():
        dic['name'] = 1
    else:
        dic['name'] = 2
    response = JsonResponse(dic, content_type='application/json;charset=utf-8')
    return response


def qiut(request):
    # 安全退出的权限要删除session
    session = request.session['logined']
    if not session:  # 如果没有session 说明没有登录，跳转到登陆界面
        return redirect('store/login/')
    else:
        request.session.clear()  # 报错：'WSGIRequest' object has no attribute 'sessoin' ,单词写错了
        return HttpResponse('您已经安全退出了')

    #添加 店铺 ，店铺与卖家seller 是一对一的关系

    #增加店铺
class Add_store(MyDecoratorMixinLogin,MyDecoratorMixinStore,View):
    def get(self, request):
        storetype_list = StoreType.objects.values('id','name')
        return render(request, 'store/add_store.html',locals())

    def post(self, request):
        data = request.POST
        name = data.get('name')
        address = data.get('address')
        description = data.get('description')
        image = request.FILES.get('image')
        phone = data.get('phone')
        money = data.get('money')
        seller_id = request.session.get('logined') # 卖家和店铺是一对一的关系，一个seller_id只能用一次
        storetype_ids = data.getlist('storetype_ids')# 获取店铺类型的id,是多选的，有多个值
        store = Store.objects.create(
            name = name,
            address = address,
            description = description,
            image = image,
            phone = phone,
            money = money,
            seller_id = seller_id
        )
        for storetype_id in storetype_ids:
            #把商品对应类型加入Storetype
            store.storetype.add(StoreType.objects.filter(id=storetype_id).first())
        store.save()
        return HttpResponse("注册店铺成功")

# 编辑店铺
class Edit_store(MyDecoratorMixinLogin,View):
    def get(self, request):
        #1.根据session值获取卖家的id,因为之前创建session的值是seller_id
        seller_id = request.session.get('logined')
        #获取卖家对应Store所有值
        store = Store.objects.filter(seller_id=seller_id).first()
        #获取storetype ,返回的是多个值store.storetype.all()
        storetype_ids = [i.id for i in store.storetype.all()]
        storetype_list = StoreType.objects.values()
        return render(request,'store/edit_store.html',locals())

    def post(self, request):
        #获取修改后的内容
        data = request.POST
        id = data.get('id')
        name = data.get('name')
        address = data.get('address')
        description = data.get('description')
        image = request.FILES.get('image')
        phone = data.get('phone')
        money = data.get('money')
        storetype_ids = data.getlist('storetype_ids')
        #把修改后内容放入数据库
        store = Store.objects.filter(id=id)
        store.name  = name
        store.address  = address
        store.description  = description
        store.phone  = phone
        store.money  = money
        #判断图片有没有更改，如果修改的话就把之前的删除重新赋值，如果不修改就不变，不用重新赋值
        if image:
            os.remove(os.path.join(settings.MEDIA_ROOT,store.image.name))
            store.image = image
        # 重新给商品类型赋值
        for storetype_id in storetype_ids:
            # 把商品所属类型的内容加入到商品中
            store.storetype.add(StoreType.objects.filter(storetype_id=storetype_id).first())
        store.save()
        return HttpResponse('编辑成功')


def index(request):
    return render(request,'store/index.html')

# 添加商品
class Add_goods(MyDecoratorMixinLogin,MyDecoratorMixinStore,View):
    def get(self, request):
        goodstype_list = GoodsType.objects.values('id','name')
        return render(request, 'store/add_goods.html', locals())

    def post(self,request):
        #获取前端提交的数据
        data = request.POST
        name = data.get('name')
        price = data.get('price')
        shelflife = data.get('shelflife')
        productdate = data.get('productdate')
        image = request.FILES.get('image')
        price = data.get('price')
        number = data.get('number')
        description = data.get('description')
        goodstype_id = data.get('goodstype_ids') #返回的是多个值
        store = Store.objects.filter(seller_id=request.session.get('logined')).first()
        # 把获取到的值添加到数据库中
        goods = Goods.objects.create(
            name = name,
            price = price,
            shelflife = shelflife,
            productdate = productdate,
            image = image,
            number = number,
            description = description,
            store_id = store.id,
            goodstype_id = goodstype_id,
        )
        return render(request,'store/tip.html',{'tip':'商品添加成功'})

# 商品列表
@wrapper_logined
def list_goods(request):
    #规定显示数据条数/每页
    # page_size= 5 已经应用全局变量
    # 1. 获取请求的页码
    page_now = request.GET.get('page')
    if not page_now:
        page_now = 1
    page_now = int(page_now)
    #获取请求的关键词
    keyword = request.GET.get('keyword')
    if not keyword:
        keyword = ''
        #从数据库获取数据，模糊查询，只要包含关键词的，#is_delete=False 并且没有被删除的
    qs_goods = Goods.objects.filter(name__icontains=keyword,is_delete=False).order_by('id')
    my_paginator = Paginator(qs_goods,page_size)
    # 求总页码
    sum_page = my_paginator.num_pages
    #当前页对象，如果我们把最后一页删除了会导致找不到页码报错
    try: #如果报错
        my_page = my_paginator.page(page_now)
    except:#如果不是第一页就跳到下一页，如果是第一页就正常往下走
        # 如果get输入访问，page>总页数让page = 最后一页
        if page_now > sum_page:
            page_now = sum_page
            return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now, keyword))
        if page_now < sum_page and page_now > 1:
            return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now-1,keyword))
        else:
            page_now = 1
            return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now, keyword))
    #设置显示出的页数
    num = 3 #实际显示出num * 2 + 1 个页码
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
    page_range = my_paginator.page_range[start-1:end] #显示出的页码是奇数
    # page_range = my_paginator.page_range[start - 1:end - 1] #显示出的页码是偶数
    #获取当前页的数据内容
    list_goods = my_page.object_list
    #获取数据的总个数
    count = my_paginator.count
    #第一条数据的开始编码
    sign_start = (page_now - 1) * page_size + 1
    #最后一条
    sign_end = page_now * page_size
    if sign_end > count:
        sign_end = count
    #拼接编码
    for index,good in enumerate(list_goods):
        good.num = sign_start + index
    data = {
        'list_goods':list_goods,
        'keyword':keyword,
        'page_now':page_now,
        'my_page':my_page,
        'page_range':page_range,
        'page_size':page_size,
        'count':count,
        'sum_page':sum_page,
    }
    return render(request, 'store/list_goods.html', data)

from django.core.cache import cache
# 删除商品
class DelGoods(View,MyDecoratorMixinLogin):
    def get(self,request):
        #id 是前端通过路由的方式传过来的
        id = request.GET.get('id')
        good_cache = cache.get(id)
        #如果有缓存，删除
        if good_cache :
            good_cache.delete(id)
        page_now = request.GET.get('page')
        if not page_now:
            page_now = 1
        # 获取请求的关键词
        keyword = request.GET.get('keyword')
        if not keyword:
            keyword = ''
        good = Goods.objects.filter(id=id).first()
        #当用户请求删除数据，让数据库显示已经被删除，
        #之后的查询限制条件找出is_delete = False ,没有被删除的数据
        good.is_delete = True
        good.save()
        return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now,keyword))

#上下架商品
class UpGoods(View,MyDecoratorMixinLogin):
    def get(self,request):
        # id 是前端通过路由的方式传过来的
        page_now = request.GET.get('page')
        if not page_now:
            page_now = 1
        # 获取请求的关键词
        keyword = request.GET.get('keyword')
        if not keyword:
            keyword = ''
        ifup = Goods.objects.filter(id=id).first()
        #先从数据库获取 是否上下架
        # 1. 点击了上、下架之后调用A标签，之后再调用到本函数,然后再重新渲染返回
        if ifup.up == 1:
            ifup.up = 0
        else:
            ifup.up = 1
        ifup.save()
        return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now,keyword))

#实现页码跳转 ，input 输入框提交，url 函数，获取值，重定向赋值
class Jump(View,MyDecoratorMixinLogin):
    def get(self,request):
        page = request.GET.get('jump')

        if not page:
            page = 1
        # page_size = 5
        page = int(page)
        keyword = request.GET.get('keyword')
        if not keyword:
            keyword = ''
        qs_goods = Goods.objects.filter(name__contains=keyword).order_by('id')
        my_paginator = Paginator(qs_goods, page_size)
        # 求总页码
        sum_page = my_paginator.num_pages
        if page < 0 or page > sum_page:
            page = 1
        return redirect('/store/list_goods/?page={}&keyword={}'.format(page, keyword))


# 订单管理
class Order_List(View):
    def get(self,request):
        page_now = request.GET.get('page')
        if not page_now:
            page_now = 1
        page_now = int(page_now)
        keyword = request.GET.get('keyword')
        if not keyword:
            keyword = ''
        #显示出这个店铺的所有卖出的商品
        #session的值是卖家的id根据卖家id找到对应的店铺id
        seller_id = request.session.get('logined')
        store = Store.objects.filter(seller_id=seller_id).first()
        #获取店铺所有商品
        goods = Goods.objects.filter(store=store)
        #获取该店铺所有订单详情
        orderdetail = OrderDetail.objects.filter(goods__name__icontains=keyword,goods__in=goods)
        # 分页
        page_size = 2
        my_paginator = Paginator(orderdetail, page_size)
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
            if page_now < sum_page and page_now > 1:
                return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now - 1, keyword))
            else:
                page_now = 1
                return redirect('/store/list_goods/?page={}&keyword={}'.format(page_now, keyword))
        # 设置显示出的页数
        num = 1 # 实际显示出num * 2 + 1 个页码
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
        orderdetail_list = my_page.object_list
        # 获取数据的总个数
        count = my_paginator.count
        # 第一条数据的开始编码
        sign_start = (page_now - 1) * page_size + 1
        # 最后一条
        sign_end = page_now * page_size
        if sign_end > count:
            sign_end = count
        # 拼接编码 ,索引0开始和遍历的值
        for index, orderdetail in enumerate(orderdetail_list):
            orderdetail.num = sign_start + index
        data = {
            'orderdetail_list': orderdetail_list,
            'page_now': page_now,
            'my_page': my_page,
            'page_range': page_range,
            'page_size': page_size,
            'count': count,
            'sum_page': sum_page,
        }
        return render(request,'store/order_list.html',data)

# 发货
class Order_Send(View):
    def post(self,request):
        orderdetail_id = request.POST.get('orderdetail_id')

        print(orderdetail_id)

        ordersdetail = OrderDetail.objects.filter(id=orderdetail_id).first()
        order = Order.objects.filter(id=ordersdetail.order_id).first()
        order.status = 3
        order.save()
        # data = {
        #     'ordersdetail':ordersdetail.order.status
        # }
        return JsonResponse({})


# 缓存
def t2(request):
    goods = Goods.objects.all()
    lis = []
    for good in goods:
        dic = {}
        dic.update(good_id=good.id)
        dic.update(good_name=good.name)
        lis.append(dic)
    print(lis)
    return render(request,'store/t2.html',{'lis':lis})


