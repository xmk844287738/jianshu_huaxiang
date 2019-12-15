
# my_dict = {'name': '666', 'name': '666', 'namefsds': '6666'}
#
# print(my_dict.keys())

# 差值表达式
# HW = 'Hello World'
# t1 = 6
# print(f'{HW} {t1}')

# site= {'name': '我的博客地址', 'alexa': 10000, 'url':'http://blog.csdn.net/uuihoo/'}
# print(site)
# # del site['name'] # 删除键是'name'的条目
# # print(site)

# word_list = ['读', '读书1', '读书']
# word_dict = {'读':1, '读书':3}
# key_word = '阅读'
# # for i in range(len(word_list)):
# #     print(word_list[i])
#
# for i in word_list:
#     if i in word_dict:
#         print('666')

# word_list = [('读', '读书', '朗读'), ('旅行',)]
# for word_tup in word_list:
#     for word in word_tup:
#         print(word)
#
#     print('*' * 60)

# 查看 内核CPU 核数
# import multiprocessing
# print(multiprocessing.cpu_count())

import pymongo
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
# jianshu_huaxiang 数据库名
db = client['jianshu_huaxiang']
# site 集合表名 存放用户文章
collection_UA = db['site']

res = collection_UA.aggregate([{"$match": {'user_homepage': 'https://www.jianshu.com/u/3085ce78c719'}}, {"$project": {"cnt": {"$size":"$user_article"}}}])

# count => cnt
# num = res[0]['cnt']
# print(res[0]['cnt'])
res_list = list(res)
# print(res_list[0]['cnt'])

for item, key in res_list[0].items():
    print(f"'{item}':{key}")