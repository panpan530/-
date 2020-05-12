from django.test import TestCase
import  pymysql
import random

def addgoods():
    my_connect = pymysql.connect(host='127.0.0.1',user='root',password='',database='shopff', port=3306,charset='utf8')
    my_cursor = my_connect.cursor()

    for i in range(1,7):
        for j in range(100):
            sql = 'INSERT INTO shop_goods' \
                  '(create_time,' \
                  'update_time,' \
                  'is_delete,' \
                  'name,' \
                  'price,' \
                  'image,' \
                  'number,' \
                  'description,' \
                  'productdate,' \
                  'shelflife,' \
                  'up,' \
                  'goodstype_id,' \
                  'store_id,' \
                  'sales,' \
                  'unite)' \
                  'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            my_cursor.execute(sql,[
                # str(i)+str(j),random.randint(1,10000),'img/goods.jpg',random.randint(1,10000),'好的很','2019-10-10',random.randint(1,10000),2,i,1,'500g',random.randint(1,10000),'2019-10-10','2019-10-10',0,random.randint(1,10000)])
                '2019-10-10',
                '2019-10-10',
                0,
                str(i)+str(j),
                random.randint(1,10000),
                'goods.jpg',
                random.randint(1,10000),
                '好的很',
                '2019-10-10',
                random.randint(1,10000),
                1,
                random.randint(1,6),
                1,
                random.randint(1,10000),
                '500g'
                ])
            my_connect.commit()
    my_cursor.close()
    my_connect.close()
    print('OK')

if __name__ == '__main__':
    # test1()
    # test2()
    # test3()
    addgoods()

