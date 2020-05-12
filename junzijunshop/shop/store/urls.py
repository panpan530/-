from django.urls import path
from store.views import *
from store.util import *
urlpatterns = [
    path('register/',Register.as_view()),
    path('login/',Login.as_view()),
    path('check_name/',check_name),
    path('qiut/',qiut),
    path('index/',index),
    path('add_store/',wrapper_logined(Add_store.as_view())),
    path('edit_store/',wrapper_logined(Edit_store.as_view())),
    path('add_goods/',Add_goods.as_view()),
    path('list_goods/',wrapper_logined(list_goods)),
    path('up_goods/',wrapper_logined(UpGoods.as_view())),
    path('del_goods/',wrapper_logined(DelGoods.as_view())),
    path('jump/', wrapper_logined(Jump.as_view())),
    path('order_list/', wrapper_logined(Order_List.as_view())),
    path('order_send/', wrapper_logined(Order_Send.as_view())),
    path('t2/', t2),

]