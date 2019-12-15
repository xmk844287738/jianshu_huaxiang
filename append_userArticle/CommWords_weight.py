
# 处理用户的常用词及从用词的出现次数

from collections import Counter
import pymongo
from append_userArticle.jieba_cut import articles_common_words


def user_commWords_weight(user_homepage=None, limit=500, skip=0):
    """
    根据输入的 user_homepage 对用户的文章,利用 jieba库 进行分词，并统计出用户每篇文章常用词、用户前100常用词；
    对应前100常用词的出现次数存入 commonWords_v5 集合
    :param user_homepage:
    :return:
    """

    # 连接 mongoDB数据库
    client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    # jianshu_huaxiang 数据库名
    db = client['jianshu_huaxiang']
    # site 集合表名 存放用户文章
    collection_UA = db['site']

    # 常用词 集合表名 存放用户常用词及常用词权重
    collection_CW_v5 = db['commonWords_v5']

    if user_homepage:
        res = collection_UA.find({'user_homepage': user_homepage})
    else:
        res = collection_UA.find().limit(limit).skip(skip)

    # 遍历得到用户对象
    for user in res:
        print(user['nickname'])
        # 作者常用词列表
        user_commonWords = []
        # print(user['user_homepage'])
        # 将数据库当前前用户的 nickname 、user_homepage 拼接成字典类型
        user_infro = {}
        user_infro['nickname'] = user['nickname']
        user_infro['user_homepage'] = user['user_homepage']
        user_infro['gender'] = user['gender']
        # 为处理 文章分词开辟新的 列表空间
        user_infro['article_commonWords'] = []

        # 以用户常用词作为 key, 用户常用词出现的次数作为 value
        user_infro['user_commonWords'] = []

        # 用户信息数据提交数据库，新增至 commonWords 集合
        collection_CW_v5.insert_one(user_infro)

        user_article = user['user_article']
        # 每篇文章的常用词
        top_words = 50
        for piece in range(len(user_article)):
            # 一篇文章的常用词
            user_article_first = user_article[piece]['content']  # 文章内容
            title = user_article[piece]['title']  # 文章标题

            if piece % 10 == 0:
                print("第{piece}篇:".format(piece=piece + 1))
            top_word_list = articles_common_words(user_article_first, top_words)
            article_commonWords = []
            # 遍历 top_word_list列表 整合为str类型对象
            for j in range(len(top_word_list)):
                # print(str(top_word_list[j][0]), end=',')
                article_commonWords.append(top_word_list[j][0])

                # 作者常用词
                user_commonWords.append(top_word_list[j][0])

            # print(' '.join(article_uselyWords))
            # 提交保存当前用户文章的常用词
            article = {}
            article['title'] = title
            # article['common_words'] = str(article_commonWords)
            article['common_words'] = ','.join(article_commonWords)
            user_homepage = user_infro['user_homepage']
            collection_CW_v5.update_one({"user_homepage": user_homepage},
                                        {"$addToSet": {"article_commonWords": {"$each": [article]}}})

        counter = Counter(user_commonWords)
        list_words = counter.most_common()
        # print(list_words[:100])
        user_commonWords_dict = {}
        # list_words 列表套元组 100项中每一项 转为字典对象 存入commonWords_v4 集合表
        for item in list_words[:100]:
            commWord = {}
            # 以用户常用词作为 key, 用户常用词出现的次数作为 value
            commWord[item[0]] = item[1]
            collection_CW_v5.update_one({"user_homepage": user_homepage},
                                        {"$addToSet": {"user_commonWords": {"$each": [commWord]}}})

            user_commonWords_dict[item[0]] = item[1]

        # print(user_commonWords_dict)

        # 把 user_commonWords_dict 更新至 commonWords_v5 集合
        collection_CW_v5.update_one({"user_homepage": user_homepage}, {"$set": {"user_commonWords_dict": user_commonWords_dict}})



if __name__ == '__main__':
    user_homepage = 'https://www.jianshu.com/u/b8f58ffc3272'
    user_commWords_weight(user_homepage)