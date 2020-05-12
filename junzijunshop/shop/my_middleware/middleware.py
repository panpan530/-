from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.shortcuts import render
from buyer.models import GoodsRelave
from store.models import Goods
import datetime,time

class MyMiddleware(MiddlewareMixin):
    """
    自定义中间件，需要继承MiddlewareMixin
    以下5个方法名字固定，参数固定
    """
    def process_request(self, request):
        """
        在路由url匹配之前调用
        :param request: 请求对象
        """
        # print('----------------------process_request----------------------',request.get_full_path())

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        在视图view函数执行之前调用
        :param request:请求对象
        :param view_func:视图函数
        :param view_args:视图函数的位置参数，元组格式
        :param view_kwargs:视图函数的关键字参数，字典格式
        :return:
        """

        #判断上一个路由是否为详情页的路由，如果是，给这个商品添加结束时间
        #在进入详情时先判断有没有结束时间，有就不添加开始时间，因为第一次的浏览时长最具有代表性
        #没有则添加开始时间，页面跳转到别的页面之后就在这里添加了结束时间。
        #缺点是：如果只有一个页面就无法获取访问结束时间，最后一个页面也无法知道结束时间，
                #一个人页面停留时间很长没有获取下一个页面，造成异常数据
        #保存本次请求url和user_id,在前面判断有没有这个url有的话就添加结束时间

        from redis import StrictRedis
        rds = StrictRedis()

        # 获取本次请求的网址
        start_url = request.get_full_path()
        #只有详情的才经过这里
        if 'detail' in start_url:
            # 如果用户没有登录就设置buyer_id为IP
            buyer_id = request.user.id
            # print(buyer_id)
            if not buyer_id:
                buyer_id = request.get_host()

            #取出上一个url
            ahead_url = rds.get(buyer_id)
            # print(ahead_url)
            #如果是第一个请求就没有第一个url,就加在session中，还需要设置过期时间为
            if not ahead_url:
                rds.set(buyer_id,start_url,)

            # 如果有了ahead_url,就属于第二个页面，把最后的时间加入
            else:
                id = request.GET.get('goods_id')
                goods = Goods.objects.filter(id=id).first()
                if goods.id:
                    goodsrleave = GoodsRelave.objects.filter(buyer_id=buyer_id).first()
                    now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                    goodsrleave.end_time = now_time
                    goodsrleave.save()
        # print('----------------------process_view----------------------',request.get_full_path())

    def process_exception(self, request, exception):
        """
        视图函数抛出异常的时候调用
        :param request: 请求对象
        :param exception: 异常对象
        :return:
        """

        # print('----------------------process_exception----------------------',request.get_full_path())
        return HttpResponse('服务器出错')

    def process_template_response(self, request, response):
        """
        只有视图函数中使用render渲染才调用
        :param request: 视图处理完成的请求
        :param response: 视图处理完成的响应
        :return:
        """
        # print('----------------------process_template_response----------------------',request.get_full_path())
        return response

    def process_response(self, request, response):
        """
        视图函数返回response之后调用
        :param request: 视图处理完成的请求
        :param response: 视图处理完成的响应
        """
        # print('----------------------process_response----------------------',request.get_full_path())
        return response









