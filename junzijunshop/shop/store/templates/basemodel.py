from django.db import models

class Basemodel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='删除标记') #1是已经删除


    # auto_now_add表示新增对象，自动赋值当前时间：创建对象的时间
    # create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # #auto_now 更新对象时，记住更新的时间，重新赋值新的时间
    # update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # # 1 , True是已经删除，在数据库中记录是否删除，删除了用户前端是找不到，但实际上还是保留在数据库中
    # #前端查询时，后端查找数据filter筛选,default = false ,选出没有被删除的
    # is_delete = models.BooleanField(default=False, verbose_name='删除标记')


    class Meta:
        abstract = True  #只是可以被继承，但是不会映射到数据库中,继承的会被映射到数据库，但是本页面不会