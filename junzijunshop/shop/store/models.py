from django.db import models
from ckeditor.fields import RichTextField
from store.templates.basemodel import Basemodel


"""一个卖家 一个店铺 多种店铺类型 多种商品 多种商品类型  一种商品多张图片"""

    #卖家
class Seller(models.Model):
    username = models.CharField(max_length=30,verbose_name='用户名')
    password = models.CharField(max_length=100,verbose_name='密码')
    nickname = models.CharField(max_length=30,verbose_name='昵称',null=True,blank=True)
    phone = models.CharField(max_length=33,verbose_name='电话',null=True,blank=True)
    email = models.EmailField(verbose_name='邮箱',null=True,blank=True)
    image = models.ImageField(upload_to='img',verbose_name='用户头像',null=True,blank=True)
    address = models.CharField(max_length=44,verbose_name='地址',null=True,blank=True)
    cardid = models.CharField(max_length=18,verbose_name='身份证')
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '卖家'
        verbose_name_plural = '卖家'
        db_table = 'shop_seller'



    # 店铺类型和店铺
class StoreType(models.Model):
    name = models.CharField(max_length=30,verbose_name='店铺类型')
    description = models.TextField(verbose_name='店铺类型描述')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '店铺类型'
        verbose_name_plural = '店铺类型'
        db_table = 'shop_storetype'

from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
  #店铺  与 店铺类型建立一对多的关系，与卖家简历一对一的关系
class Store(models.Model):
    name = models.CharField(max_length=30,verbose_name='店铺名称')
    address = models.CharField(max_length=30,verbose_name='发货地址')
    description = RichTextUploadingField(verbose_name='店铺描述')
    image = models.ImageField(verbose_name='LOGO',upload_to='img')
    phone = models.CharField(max_length=11,verbose_name='电话')
    money = models.FloatField(verbose_name='注册资金')
    seller = models.OneToOneField(to=Seller,on_delete=models.CASCADE,verbose_name='所属卖家')
    storetype = models.ManyToManyField(to=StoreType,verbose_name='店铺类型')

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        db_table = 'shop_store'


    # 商品类型，与商品多对多的关系
class GoodsType(models.Model):  # 物品的类型 与 物品是一对多的关系
    name = models.CharField(max_length=32, verbose_name='商品类型')
    description = models.TextField(max_length=32, verbose_name='商品类型描述')
    picture = models.ImageField(upload_to='buyer/images')

    class Meta:
        verbose_name = '商品类型'
        verbose_name_plural = '商品类型'
        db_table = 'shop_goodstype'
  #商品  与 店铺建立多对多的关系 ， 与商品类型建立一对多的关系，一种 类型有多种商品

class Goods(Basemodel):
    name = models.CharField(max_length=32, verbose_name='商品名称')
    price = models.FloatField(verbose_name='价格')
    image = models.ImageField(upload_to='img', verbose_name='图片')
    number = models.IntegerField(verbose_name='库存')
    description = models.TextField(verbose_name='描述')
    productdate = models.DateField(verbose_name='生产日期')
    shelflife = models.IntegerField(verbose_name='保质期')
    store = models.ForeignKey(to=Store,on_delete=models.CASCADE, verbose_name='所属店铺') #建立外键表有店铺的id 和 商品的id
    goodstype = models.ForeignKey(to=GoodsType,on_delete=models.CASCADE,verbose_name='商品类型')
    up = models.IntegerField(verbose_name='商品上下架',default=0) # 0 是下架，1是上架
    sales = models.IntegerField(verbose_name='销量',null=True)
    unite = models.CharField(default='500g', max_length=20, verbose_name='单位')


    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        db_table = 'shop_goods'


   # 商品图 与 商品是一对多的关系 一个商品有多张图片
class GoodsImg(models.Model): #商品图片upload_to='img'上传后的储存路径
    image = models.ImageField(upload_to='img', verbose_name='图片地址')
    description = models.TextField(max_length=32, verbose_name='图片描述')
    goods = models.ForeignKey(to=Goods, on_delete=models.CASCADE, verbose_name='所属商品')

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = '商品图片'
        db_table = 'shop_goodsimg'







