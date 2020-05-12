from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def func(data,key,expires): #参数：要加密的数据，钥匙，和过期的时间
    #创建加密对象
    myserializer = Serializer(key,expires)
    #加密
    mi_data = myserializer.dumps(data).decode()
    return mi_data

def en_func(data,key,expires): #参数：要解密的数据，钥匙，和过期的时间
    myserializer = Serializer(key,expires)
    en_mi = myserializer.loads(data)
    return en_mi