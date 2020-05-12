from django.urls import path,re_path,include
from buyer.views import *
from django.contrib.auth.models import User
from rest_framework import routers
from store.models import Goods
from django.conf.urls import url, include


urlpatterns = [
    path('login/', Login.as_view()),
    path('register/', Register.as_view()),
    path('active/', Active.as_view()),
    path('index/', Index.as_view()),
    path('detail/', Detail.as_view()),
    path('user_center_info/', User_center_info.as_view()),
    path('user_center_order/', User_center_order.as_view()),
    path('user_center_site/', User_center_site.as_view()),
    path('list/', List.as_view()),
    path('readmore/', Readmore.as_view()),
    path('add_cart/', Add_cart.as_view()),
    path('cartlist/', CartList.as_view()),
    path('cart_delete/', Cart_delete.as_view()),
    path('cart_update/', Cart_Update.as_view()),
    path('place_order/', Place_Order.as_view()),
    path('oder_submit/', Order_Submit.as_view()),
    path('order_pay/', Order_Pay.as_view()),
    path('pay_result/', Pay_Result.as_view()),
    path('tb/', Table.as_view()),

]

from rest_framework import routers

router = routers.DefaultRouter()
router.register('history_api', GoodsViewSet)
router.register('echarts_api',EchartsViewSet)
router.register('goodstype_api',GoodsTypeViewSet)

urlpatterns+=router.urls














