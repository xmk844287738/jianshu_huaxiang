import pymongo

# 连接指定的 mongodb jianshu_huaxiang 数据库里的 site 集合
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")

# jianshu_huaxiang 数据库名
db = client['jianshu_huaxiang']

# site 集合表名
mycollection = db['site']

class Storage(object):
    """存储数据"""

    def __init__(self):
        self.user_homepage = ''



    # 使用 @ staticmethod或 @ classmethod，就可以不需要实例化，直接类名.方法名()来调用。
    @classmethod
    def save_to_mongodb(self, user_infro, user_homepage):
        """ user_infro 字典类型的数据 user_homepage 用户主页 字符串类型"""
        self.user_homepage = user_homepage

        try:
            # 数据提交数据库
            mycollection.insert_one(user_infro)
        except Exception as e:
            print(e)
            # raise RuntimeError('保存至数据库过程Error！')
            print('保存至数据库过程Error！')

    @classmethod
    def update_to_mongodb(self, article):
        """  根据 user_homepage 用户主页 匹配保存 获取到的 当前用户文章 """
        try:
            # 数据提交数据库
            # mycollection.update_one({'user_homepage': self.user_homepage}, {'$set': article})
            # 根据 user_homepage 用户主页 匹配保存 获取到的 当前用户文章
            mycollection.update_one({"user_homepage": self.user_homepage}, {"$addToSet": {"user_article": {"$each": [article]}}})
        except Exception as e:
            print(e)
            # raise RuntimeError('保存至数据库过程Error！')
            print('保存至数据库过程Error！')


    @classmethod
    def allarticle_to_mongodb(self, article):
        """  保存用户所有的文章  article  大字典 """
        try:
            # 用户所有文章的数据提交数据库
            mycollection.update_one({"user_homepage": self.user_homepage},
                                    {"$set": article})
        except Exception as e:
            print(e)
            # raise RuntimeError('保存至数据库过程Error！')
            print('保存至数据库过程Error！')


