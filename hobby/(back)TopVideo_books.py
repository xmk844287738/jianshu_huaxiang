from collections import Counter
import pymongo
import re

# 600名用户中，出现次数最多的前100个视频名字、出现次数最多的前100个书籍名字

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
# jianshu_huaxiang 数据库名
db = client['jianshu_huaxiang']
# site 集合表名
mycollection = db['site']


def get_topVideo_Books(user_homepage=None, gender='none', num=600, skip=0):
    """
    gender 为 None 进行 findall 模式查找  (None 不等于字符串 'none') 返回值：video_top100 字典对象 前100名视频的名字; books_top100 字典对象 前100名书籍的名字
    :param gender: 性别
    :param num: 数据库里前 num 个记录
    :param skip: 是否启用跳过前num过用户
    :return: video_top100 => 字典, books_top100 => 字典
    """
    video_str = ''
    with open('../hobby/video_name.txt', 'r', encoding='utf-8') as f:
        video_str = f.read()

    f.close()

    video_list = video_str.split('\n')
    # 初始化各视频名称的次数为0
    video_index = [0 for i in range(len(video_list))]

    # 以视频名称为 key 关键字； 值为 各视频出现的次数
    video_dict = {}
    for name, count in zip(video_list, video_index):
        video_dict[name] = count

    # 按照用户主页查询（user_homepage）
    user_homepage = user_homepage
    if user_homepage != None:
        print('user_homepage:' + str(user_homepage))
        res = mycollection.find({'user_homepage': user_homepage})

    # 读取mongoDb数据库里 前num个用户
    elif gender:
        # 规定性别查找
        res = mycollection.find({'gender': gender}).limit(num).skip(skip)

    else:
        res = mycollection.find().limit(num).skip(skip)

    # 存放用户的书籍名称
    bookNames = []
    # 遍历得到用户对象
    for user in res:
        user_every_article = user['user_allarticle']
        # 正则表达式匹配 书名号
        match_rule = re.compile(r'《\w+[\u4e00-\u9fa5]+\w+》')
        result = match_rule.findall(user_every_article)  # 返回一个列表类型变量
        # 去掉字符串两端的书名号 《》
        result = list(map(lambda x: x.strip('《》'), result))
        if result:
            for worksName in result:
                if worksName in video_list:
                    video_dict[worksName] += 1

                else:
                    bookNames.append(worksName)

    video_top = sorted(video_dict.items(), key=lambda video_dict: video_dict[1], reverse=True)

    # 把 video_top 列表元组转化为 字典对象
    video_top100 = {}
    for item in video_top[:100]:
        video_top100[item[0]] = item[1]

    # # 600名用户中，出现次数最多的前100个视频名字
    # print(video_top[:100])
    #
    # # 600名用户中，出现次数最多的前100个书籍名字
    # print(Counter(bookNames).most_common(100))

    books_top = Counter(bookNames).most_common(100)
    # 把 books_top 列表元组转化为 字典对象
    books_top100 = {}
    for item in books_top[:100]:
        books_top100[item[0]] = item[1]

    return video_top100, books_top100


if __name__ == '__main__':
    video_top100, books_top100 = get_topVideo_Books(gender=None, num=600, skip=0)
    print(video_top100)
    print(books_top100)