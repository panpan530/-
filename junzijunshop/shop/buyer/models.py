from django.db import models
from store.templates.basemodel import *
from django.contrib.auth.models import AbstractUser
from store.models import *

class Buyer(Basemodel,AbstractUser):
    # 继承了AbstractUser有的字段
    phone = models.CharField(max_length=32,verbose_name='电话',blank=True,null=True)
    addr = models.CharField(max_length=32,verbose_name='联系地址',blank=True,null=True)

    class Meta:
        verbose_name_plural = '买家'
        verbose_name = '买家'
        db_table = 'shop_buyer'


class Discount(models.Model):
    goods_discount = models.PositiveIntegerField(default=0, verbose_name='折扣')
    goods_coupon = models.PositiveIntegerField(default=0, verbose_name='商品折扣')
    store_coupon = models.PositiveIntegerField(default=0, verbose_name='店铺折扣')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    goods = models.OneToOneField(to=Goods, on_delete=models.CASCADE)
    buyer = models.ForeignKey(to=Buyer,on_delete=models.CASCADE)
    store = models.ForeignKey(to=Store,on_delete=models.CASCADE)


class Address(Basemodel):
    name = models.CharField(max_length=32, verbose_name='收货人姓名')
    password = models.CharField(max_length=32, verbose_name='收货地址邮编')
    phone = models.CharField(max_length=32, verbose_name='收货人电话')
    addr = models.CharField(max_length=32, verbose_name='收货地址')
    buyer = models.ForeignKey(to=Buyer,on_delete=models.CASCADE,verbose_name='收货地址')
    isdefault = models.BooleanField(default=True, verbose_name='是默认地址')

    class Meta:
        verbose_name_plural = '收货地址'
        verbose_name = '收货地址'
        db_table = 'shop_address'

class Cart(Basemodel):
    goods = models.ForeignKey(to=Goods, on_delete=models.CASCADE, verbose_name='所属商品')
    count = models.IntegerField(verbose_name='数量') #购物车所有商品的数量
    buyer = models.ForeignKey(to=Buyer, verbose_name='所属用户', on_delete=models.CASCADE)

    def __str__(self):
        return self.buyer.username + '-' + self.goods.name

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        db_table = 'shop_cart'


#count 是一次付款的所有商品的总数 一次下单6件商品，count是6
class Order(Basemodel):
    ORDER_PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付')
    )
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )
    id = models.CharField(max_length=128, primary_key=True, verbose_name='订单id')
    buyer = models.ForeignKey(to=Buyer, on_delete=models.CASCADE, verbose_name='用户')
    address = models.ForeignKey(to=Address, on_delete=models.CASCADE, verbose_name='地址')

    paymethod = models.IntegerField(choices=ORDER_PAY_METHOD_CHOICES, default=3, verbose_name='支付方式')
    totalcount = models.IntegerField(default=0, verbose_name='商品数量')
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name='订单运费')
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    paynumber = models.CharField(max_length=128, default='', verbose_name='支付编号')

    class Meta:
        db_table = 'shop_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name

#count 是一个商品的数量
class OrderDetail(Basemodel):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name='所属订单')
    goods = models.ForeignKey(to=Goods, on_delete=models.CASCADE, verbose_name='所属商品')
    count = models.IntegerField(verbose_name='商品数量')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    name = models.CharField(max_length=32, verbose_name='名称')
    image = models.ImageField(upload_to='img', verbose_name='图片')
    unite = models.CharField(default='500g', max_length=20, verbose_name='单位')

    class Meta:
        db_table = 'shop_orderdetail'
        verbose_name = '订单详情'
        verbose_name_plural = verbose_name


class GoodsRelave(models.Model):
    views = models.PositiveIntegerField(default=0,verbose_name='点击量')
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    goods = models.OneToOneField(to=Goods, on_delete=models.CASCADE)
    buyer = models.ForeignKey(to=Buyer,on_delete=models.CASCADE)


# 有搜索的界面就要给这个表加关键词，下单的地方加order_id
class KeyWord(models.Model):
    keyword = models.CharField(null=True, max_length=200, verbose_name='关键字')
    key = models.ManyToManyField(to=Buyer,null=True,blank=True)
    order = models.ManyToManyField(to=Order,null=True,blank=True)









