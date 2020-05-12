
from django_filters.rest_framework import *
from buyer.models import *
from store.models import *


class Goodsfilter(FilterSet):
#     'name', 'price', 'image', 'number','description', 'store', 'sales', 'unite'
    number = NumberFilter(field_name='number', lookup_expr='gte', help_text='库存')
    price = NumberFilter(field_name='price', lookup_expr='lte', help_text='价格')
    sales = NumberFilter(field_name='sales', lookup_expr='gte', help_text='销量')
    name = CharFilter(field_name='name', lookup_expr='icontains', help_text='根据名字模糊查询')















