from store.models import Goods,GoodsType
from buyer.models import GoodsRelave
from rest_framework.serializers import  ModelSerializer


class GoodsSerializer(ModelSerializer):
    class Meta:
        model = Goods
        fields = ['id','name', 'price', 'image', 'number','description', 'store', 'sales', 'unite','goodstype_id'
                  ]


class EchartsSerializer(ModelSerializer):
    class Meta:
        model = GoodsRelave
        fields = ['views', 'end_time']



class GoodsTypeSerializer(ModelSerializer):
    class Meta:
        model = GoodsType
        fields = ["id",'name'
                  ]