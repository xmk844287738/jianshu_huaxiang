import re
import os
from collections import Counter
import pymongo
from wordcloud import WordCloud, ImageColorGenerator
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np



class user_wordCloud:

    def __init__(self):

        curPath = os.path.abspath(os.path.dirname(__file__))
        # 获取jianshu_flask，也就是项目的根路径
        projectPath = curPath[:curPath.find("jianshu_flask\\") + len("jianshu_flask\\")]

        self.projectPath = projectPath

        # 连接 mongoDB 数据库

        client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
        db = client['jianshu_huaxiang']
        # 修改 commonWords_v3 集合 合并为 commonWords_v4 集合！！！！
        collection_CW = db['commonWords_v3']
        self.collection_CW = collection_CW

        # site 作者文章集合表名
        collection_UA = db['site']
        self.collection_UA = collection_UA

        # 用户主页
        self.user_homepage = None

    # 简书用户常用词
    def get_commonWords(self, user_homepage=None, gender='none', num=600, skip=0):
        """
        gender 为 None 进行 findall 模式查找  (None 不等于字符串 'none') 返回值：userCommWords_top100 字典对象 key:常用词； value：常用词出现的次数
        :param gender: 性别
        :param num: 数据库里前 num 个记录
        :param skip: 是否启用跳过前num过用户
        :return:userCommWords_top100 字典对象
        """
        # 存放常用词
        commonWords = []

        # 按照用户主页查询（user_homepage）
        self.user_homepage = user_homepage
        if self.user_homepage != None:
            # print('user_homepage:' + str(self.user_homepage))
            res = self.collection_CW.find({'user_homepage': self.user_homepage})

        # 按照用户群体查询（性别类型）
        # 读取mongoDb数据库里 前num个用户
        elif gender:
            # 规定性别查找
            res = self.collection_CW.find({'gender': gender}).limit(num).skip(skip)

        else:
            res = self.collection_CW.find().limit(num).skip(skip)

        for user in res:
            user_commonWords = user['user_commonWords'].split(',')
            for words in user_commonWords:
                commonWords.append(words)

        userCommWords = Counter(commonWords).most_common(100)
        # 把 userCommWords_top100 列表元组转化为 字典对象
        userCommWords_top100 = {}
        for item in userCommWords:
            userCommWords_top100[item[0]] = item[1]

        return userCommWords_top100

    # 在所选的用户中，出现次数最多的前100个视频名字、出现次数最多的前100个书籍名字
    def get_topVideo_Books(self, user_homepage=None, gender='none', num=600, skip=0):
        """
        gender 为 None 进行 findall 模式查找  (None 不等于字符串 'none') 返回值：video_top100 字典对象 前100名视频的名字; books_top100 字典对象 前100名书籍的名字
        :param gender: 性别
        :param num: 数据库里前 num 个记录
        :param skip: 是否启用跳过前num过用户
        :return: video_top100 => 字典, books_top100 => 字典
        """
        video_str = ''
        # 获取video_name.txt文件的路径 (hobby 文件夹下的video_name.txt)
        video_namePath = os.path.abspath(self.projectPath + 'hobby\\video_name.txt')

        with open(video_namePath, 'r', encoding='utf-8') as f:
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
        self.user_homepage = user_homepage
        if self.user_homepage != None:
            print('user_homepage:' + str(self.user_homepage))
            res = self.collection_UA.find({'user_homepage': user_homepage})

        # 按照用户群体查询（性别类型）
        # 读取mongoDb数据库里 前num个用户
        elif gender:
            # 规定性别查找
            res = self.collection_UA.find({'gender': gender}).limit(num).skip(skip)

        else:
            res = self.collection_UA.find().limit(num).skip(skip)

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


    # 根据用户常用词、用户喜爱书籍 Top 100 两份数据生成词云图
    def user_wordcloud(self, words_dict, filname, tofile, max_font_size, min_font_size):
        """
        根据用户常用词、用户喜爱书籍 Top 100 两份数据生成词云图
        :param words_dict:
        :param filname: 要依据那副图片进行词云设计
        :param tofile: 生成词云的图片名字
        :param max_font_size: 显示的最大的字体大小
        :param min_font_size: 显示的最小的字体大小
        :return:
        """
        images = Image.open(filname)
        maskImages = np.array(images)

        ##修改了一下wordCloud参数,就是把这些数据整理成一个形状,
        ##具体的形状会适应你的图片的.

        # 获取 方正字迹-曾正国楷体.TTF文件的路径 (jianshu_huaxiang 文件夹下的方正字迹-曾正国楷体.TTF)
        fontPath = os.path.abspath(self.projectPath + 'jianshu_huaxiang\\方正字迹-曾正国楷体.TTF')

        wc = WordCloud(font_path=fontPath, background_color="white", max_font_size=max_font_size,
                       min_font_size=min_font_size,
                       mask=maskImages).fit_words(words_dict)

        # # #产生背景图片，基于彩色图像的颜色生成器
        # image_colors = ImageColorGenerator(maskImages)
        #
        # # 将词云颜色改为背景的颜色
        # wc.recolor(color_func=image_colors)

        plt.imshow(wc)

        # 生成词云图片的名字及路径
        wc.to_file(tofile)
        # 可以查看生成的词云图片
        plt.axis('off')
        plt.show()




if __name__ == '__main__':
    # 生成用户常用词和用户喜爱书籍（ Top 100） 的一张词云图
    user_homepage = 'https://www.jianshu.com/u/3085ce78c719'
    user_wordcloud = user_wordCloud()
    # userCommonWords = user_wordcloud.get_commonWords(user_homepage=user_homepage, gender='none', num=600)
    userCommonWords = user_wordcloud.get_commonWords(gender='none', num=600)
    # print(userCommonWords)

    top_video100, top_books100 = user_wordcloud.get_topVideo_Books(gender='none', num=600)
    # print(top_books100)
    # print(top_video100)
    # # 简书用户喜爱书籍 top_books100
    # # ** ，解包思想 合并两个字典
    CommonW_TopBooks = {**userCommonWords, **top_books100}
    # print(CommonW_TopBooks)
    user_wordcloud.user_wordcloud(CommonW_TopBooks, 'woman.jpg', 'test.jpg', 40, 3)
