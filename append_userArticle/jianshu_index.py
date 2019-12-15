from lxml import html
import time
import requests
import threading
from queue import Queue
from pyquery import PyQuery as pq
import random
import chardet
from append_userArticle.storage import Storage
from append_userArticle.tools import DecodingUtil
import pymongo

# 连接指定的 mongodb jianshu_huaxiang 数据库里的 site 集合
client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")

# jianshu_huaxiang 数据库名
db = client['jianshu_huaxiang']

# site 集合表名
mycollection = db['site']

etree = html.etree


# 获取文章的请求头
headers = {
    'x-pjax': 'true',
    'referer': 'https://www.jianshu.com/',
    'Content-Type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/77.0.3865.120 Safari/537.36',
    'x-csrf-token': 'PRFNi9/FDZmm/bV4f8ZueVNFln0PpQ5kgsMcSERpwpNugy/bcOBgNEZvBo4/aTwrm28awdmuTfcMaHcogJ1mdA=='
}


index_header = {
'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
 'Host': 'www.jianshu.com',
 'Accept-Encoding': 'gzip, deflate, sdch',
 'X-Requested-With': 'XMLHttpRequest',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
 'Connection': 'keep-alive',
 'Referer': 'https://www.jianshu.com'
}

address = 'https://www.jianshu.com'  # 简书网地址




class JianshuSpider(object):
    """爬取简书首页数据的爬虫类"""
    def __init__(self, user_homepage):
        self.max_page = 0  # 爬取总文章数：300*9=2100
        self.params_queue = Queue()  # 存放地址发送post请求参数的队列
        self.url_queue = Queue()  # 存放文章url的队列
        self.index_queue = Queue()  # 存放首页响应的新文章列表的队列
        self.article_queue = Queue()  # 存放文章响应内容的队列
        self.content_queue = Queue()  # 存放格式化后的文章数据内容的队列

        # 存放用户所有文章列表
        self.content_list = []

        # # 用户的所有文章数
        self.user_article_count = 0

        # 记录用户文章入库数
        self.temp = 0

        # 存放用户主页的地址 具有唯一性
        # self.user_homepage = index_address
        self.user_homepage = user_homepage

    # 不带参数请求的方式
    def get(self, url, url_headers):
        try:
            res = requests.get(url=url, headers=url_headers)
            return res
        except:
            self.get(url, url_headers)

    # 带参数请求的方式
    def get_data(self, url, data, url_headers):
        try:
            res = requests.get(url=url, data=data, headers=url_headers)
            return res
        except:
            self.get_data(url, data, url_headers)

    def get_params_list(self):
        """构造post请求的page参数队列"""
        # 根据self.user_article_count 用户的所有文章数 构建请求的 page参数队列
        self.max_page = int(self.user_article_count / 9) + 3
        for i in range(1, self.max_page):
            self.params_queue.put({'page': i})

    def pass_post(self):
        """发送POST请求，获取新的文章列表，请求参数从队列中取出"""
        while True:
            # 解析用户主页的文章列表
            response = self.get_data(self.user_homepage, self.params_queue.get(), headers)
            self.index_queue.put((response.content).decode(encoding='utf-8'))  # 返回结果放入队列
            self.params_queue.task_done()  # 计数减一
            print('pass_post', '@'*10)
            # t = random.randint(1, 3)
            # time.sleep(t)

    def parse_url(self):
        """根据首页返回的新的文章列表，解析出文章对应的url 9篇文章"""
        while True:
            content = self.index_queue.get()  # 从队列中取出一次POST请求的文章列表数据
            html = etree.HTML(content)
            a_list = html.xpath('//a[@class="title"]/@href')  # 每个li标签包裹着一篇文章 a_list => 9篇文章

            for a in a_list:
                url = a  # xpath解析出文章的相对路径
                article_url = address + url
                print(article_url)
                self.url_queue.put(article_url)  # 放入队列
            self.index_queue.task_done()
            print('parse_url', '@'*10)
            time.sleep(2)

    def pass_get(self):
        """发送GET请求，获取文章内容页"""
        while True:
            article_url = self.url_queue.get()  # 从队列中获取文章的url
            response = self.get(article_url, headers)
            self.article_queue.put(DecodingUtil.decode(response.content))  # 返回结果放入队列
            self.url_queue.task_done()
            print('pass_get', '@'*10)
            t = random.randint(1, 3)
            time.sleep(t)

    def get_content(self):
        while True:
            # 一篇文章
            article = dict()
            article_content = self.article_queue.get()
            html = etree.HTML(article_content)



            # 解析文章的标题
            article['title'] = html.xpath('//h1[@class="_2zeTMs"]/text()')[0].strip('\n').strip('\t')
            print(article['title'])


            # 将一篇文章的段落列表 转化为字符串
            article_paragraph = html.xpath('//article[@class="_2rhmJa"]/p/text()')   # html富文本内容
            # 段落换行
            article_content = '\n'.join(article_paragraph)
            article['content'] = article_content

            # 把当前用户的每篇文章保存到 jianshu_huaxiang 数据库里的 site 集合
            # 连接指定的 mongodb jianshu_huaxiang 数据库里的 site 集合
            Storage.update_to_mongodb(article)

            self.temp = self.temp + 1
            print("已入库的文章数/此作者的总文章数：{temp}/{user_article_count}".format(temp=self.temp, user_article_count=self.user_article_count))

            # article['content'] = DecodingUtil.decode(etree.tostring(content[0], method='html', encoding='utf-8'))

            # print(article)

            self.content_queue.put(article)  # 放入队列
            self.article_queue.task_done()  # 上一队列计数减一
            print('get_content', '@'*10)
            t = random.randint(1, 3)
            time.sleep(t)

    def save(self):
        """保存数据"""
        while True:
            article_info = self.content_queue.get()  # 队列中获取文章信息
            # print(article_info)
            # 把每篇文章添加到  用户所有文章列表 self.content_list 中
            self.content_list.append(str(article_info.get('content', '')))
            self.content_queue.task_done()
            print('save', '*'*20)
            # return content_string


    def run(self):
        """
        根据输入的 user_homepage 抓取对应用户的文章的数据信息存入 site 集合
        :return:
        """
        # 0.各个方法之间利用队列来传送数据
        # 1.简书首页加载新数据方式为POST请求，url不变，参数page变化，所以首先构造一个params集
        # 2.遍历params集发送POST请求，获取响应
        # 3.根据每一次获取的文章列表，再获取对应的真正文章内容的页面url
        # 4.向文章内容页面发送请求，获取响应
        # 5.提取对应的数据
        # 6.保存数据，一份存入数据库，一份存入excel

        # source = requests.get(self.user_homepage, headers=index_header)

        source = self.get(self.user_homepage, index_header)


        # 解析用户的总文章数
        html = etree.HTML(source.content)
        user_article_count = html.xpath('//div[@class="info"]/ul/li/div[@class="meta-block"]/a/p/text()')[2]
        # print(str(user_article_count))
        self.user_article_count = int(user_article_count)

        if (self.user_article_count < 5 or self.user_article_count > 200):
            if self.user_article_count < 5:
                print('文章数太少了！')

            if self.user_article_count > 200:
                print('文章数太多了！')

            return 'user_article_count to much'


        # 解析用户名、性别
        doc = pq(source.content)
        nickname = doc.find('.name').text()
        # head_pic = doc.find('.avatar').find('img').attr('src')
        gender = doc.find('.title').find('i').attr('class')
        if gender:
            gender = str(gender).split('-')[1]
        else:
            gender = 'none'
            # # 筛选功能
            # return 'gender is none'
        print('当前用户的性别:' + str(gender))


        # print(self.content_list)

        # 将 用户所有文章列表 content_list 通过 join 转为一个 长字符串变量 content_string
        # 除第一篇文章外，每一篇文章的 开头换行后再来一个TAB键 的缩进
        user_infro = dict()
        user_infro['gender'] = gender
        user_infro['nickname'] = nickname

        # # 把 用户主页的地址 user_homepage 传输过去，作为以后集合表 增删改查 的搜索条件
        user_infro['user_homepage'] = self.user_homepage

        # 创建用户文章的列表
        user_infro['user_article'] = []
        # self.nickname = nickname

        Storage.save_to_mongodb(user_infro, self.user_homepage)


        thread_list = list()  # 模拟线程池
        t_params = threading.Thread(target=self.get_params_list)
        thread_list.append(t_params)
        for i in range(1):  # 为post请求开启3个线程
            t_pass_post = threading.Thread(target=self.pass_post)
            thread_list.append(t_pass_post)
        for j in range(2):  # 为解析url开启3个线程
            t_parse_url = threading.Thread(target=self.parse_url)
            thread_list.append(t_parse_url)
        for k in range(3):  # 为get请求开启5个线程
            t_pass_get = threading.Thread(target=self.pass_get)
            thread_list.append(t_pass_get)
        for m in range(3):  # 为提取数据开启5个线程
            t_get_content = threading.Thread(target=self.get_content)
            thread_list.append(t_get_content)

        for n in range(3):  # 为保存数据开启5个线程
            t_save = threading.Thread(target=self.save)  # 保存数据一个线程
            thread_list.append(t_save)
        # =====================================================================================================
        for t in thread_list:
            t.setDaemon(True)  # 把子线程设置为守护线程，主线程结束，子线程结束
            t.start()
        for q in [self.params_queue, self.url_queue, self.index_queue, self.article_queue, self.content_queue]:
            q.join()  # 让主线程等待阻塞，等待队列的任务完成之后再结束

        # 用户所有文章
        user_allarticle = '\n   '.join(self.content_list)

        # 字典
        article = dict()
        article['user_allarticle'] = user_allarticle

        # 更新当前用户的信息，并存入数据库
        Storage.allarticle_to_mongodb(article)

        # print('主线程结束......')
        print('该用户的全部文章获取完成,准备下一用户文章的获取......')


def main(user_homepage):
    # # 连接指定的 mongodb jianshu_huaxiang 数据库里的 site 集合
    # client = pymongo.MongoClient("mongodb://10.25.44.132:27017/")
    #
    # # jianshu_huaxiang 数据库名
    # db = client['jianshu_huaxiang']
    #
    # # site 集合表名
    # mycollection = db['site']


    res = mycollection.find_one({'user_homepage': user_homepage})
    # res 返回 None 则开始获取
    if not res:
        print("开始获取")
        jianshu_spider = JianshuSpider(user_homepage)
        jianshu_spider.run()

    # 存在则退出，进行下一个用户文章获取
    else:
        print("该用户的文章已存在与数据库中")
        return



if __name__ == '__main__':
    # https://www.jianshu.com/u/a67ad639eb06

    user_homepage = 'https://www.jianshu.com/u/a67ad639eb06'
    main(user_homepage)


