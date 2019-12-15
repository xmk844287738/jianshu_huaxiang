from flask import Flask, render_template, request
import json
import re
import os
import pymongo
from append_userArticle.CommWords_weight import user_commWords_weight
from append_userArticle.jianshu_index import JianshuSpider
from article_num import article_num
from hobby.hobby import get_TopHobby, get_userHobby, group_huaxiang
from jianshu_huaxiang.jianshu_huaxiang import user_wordCloud



app = Flask(__name__)
# 连接 mongoDB数据库

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
# jianshu_huaxiang 数据库名
db = client['jianshu_huaxiang']
# site 集合表名 存放用户文章
collection_UA = db['site']

curPath = os.path.abspath(os.path.dirname(__file__))
# 获取jianshu_flask名称，也就是项目的根路径 （切片操作 得出项目的根路径）
# projectPath = curPath[:curPath.find("jianshu_flask\\")+len("jianshu_flask\\")]
# print(curPath)


# 测试前端 => 后端通信

# @app.route('/', methods=['GET', 'POST'])
# def get_index():
#     return render_template('index.html')


num = 10
testInfo = {}

@app.route('/recv_data', methods=['GET', 'POST'])
def recv_data():
    # receive data
    data_test = request.get_data()
    if data_test:
        # loads 字符串转化为 字典
        data_re = json.loads(data_test)
        print('email: ' + str(data_re['email']))
        print('phome: ' + str(data_re['phone']))

    else:
        print('data_test is empty')

    '''send data'''
    global num
    num = num + 1
    testInfo['name'] = 'xiaoming'
    testInfo['age'] = num
    # dumps 字典形式的数据转化为字符串
    return json.dumps(testInfo)



@app.route("/js_post/<addr>", methods=['GET', 'POST'])
def js_post(addr):
      print(addr)
      return addr +" - ip"


@app.route("/", methods=['GET', 'POST'])
def foucs():
      return render_template('crowd_huaxiang.html')


# 文本框焦点事件
@app.route('/foucs_gender/<gender>', methods=['GET'])
def foucs_gender(gender):
    # 验证输入的gender
    if gender != '' and gender != 'man' and gender != 'woman':
        # gender_error_msg = '性别输入有问题！请重新输入！（参考信息：留空或输入man或输入woman）'
        return 'false'
    return 'true'

@app.route('/foucs_user_num/<user_num>', methods=['GET'])
def foucs_user_num(user_num):
    # 验证输入的user_num
    print(user_num)
    if not user_num.isdigit():
        # 不是数字的情况
        return 'false'

    return 'true'



# 单个用户的爱好 1
@app.route('/user', methods=['GET', 'POST'])
def user_hobby():

    return render_template('user_huaxiang.html')

# 单个用户的爱好 2
# 验证 user_homepage 是否符合规则
@app.route('/user_homepage', methods=['GET', 'POST'])
def check_user_homepage():
    homepage_json = request.get_data()
    homepage_dict = json.loads(homepage_json)
    # print(homepage_dict)
    homepage = homepage_dict['homepage']

    # 使用正则验证用户输入的用户主页是否合法
    match_result = re.match(r'(https://)?(www.jianshu.com/u/)?(\w{6}|\w{12})$',
                            homepage)  # \w 匹配数字和大小写字母 例子： https://www.jianshu.com/u/485ed2eb0d8a ?=>出现0 次或多次
    # print(match_result)

    message = {}
    if match_result:  # 验证通过
        message['key_words'] = 'yes'
        # dumps 字典形式的数据转化为字符串
        return json.dumps(message)
    else:
        message['key_words'] = 'no'
        return json.dumps(message)

# 返回用户文章页数
@app .route('/user_articleNum', methods=['GET', 'POST'])
def user_articleNum():
    homepage_json = request.get_data()
    homepage_dict = json.loads(homepage_json)
    homepage = homepage_dict['homepage']

    # 根据 user_homepage 判断数据库里有无此用户的文章数据信息
    res = collection_UA.find_one({'user_homepage': homepage})
    articleNum = {}
    if res: #存在此用户
        articleNum['articleNum'] = 'yes'

    else:#不存在此用户的情况
        # 调取先前的爬取文件 解析用户的文章数
        num = article_num(homepage)
        articleNum['articleNum'] = num

    return json.dumps(articleNum)

# 单个用户的爱好 3
# 数据库里没有此用户的文章数据信息；根据 user_homepage 调取先前的爬取文件 获取用户的文章并传入数据库
@app.route('/article_Spider', methods=['GET', 'POST'])
def article_Spider():
    """
    数据库里没有此用户的文章数据信息；根据 user_homepage 调取先前的爬取文件 获取用户的文章并传入数据库
    :return:
    """
    homepage_json = request.get_data()
    homepage_dict = json.loads(homepage_json)
    homepage = homepage_dict['homepage']

    print("开始获取")
    jianshu_spider = JianshuSpider(homepage)
    jianshu_spider.run()

    # 获取完成对此用户的文章进行分词并存至 commonWords_v5 集合
    user_commWords_weight(homepage)
    message = {}
    message['key_words'] = '用户文章获取、分词完毕ok'
    return json.dumps(message)

# 单个用户的爱好 4
# 每间隔1秒钟查询 user_homepage 入库的文章数
@app.route('/everySec_queryDB', methods=['GET', 'POST'])
def everySec_queryDB():
    """
    每间隔1秒钟查询 user_homepage 入库的文章数
    :return:
    """
    homepage_json = request.get_data()
    homepage_dict = json.loads(homepage_json)
    homepage = homepage_dict['homepage']

    res = collection_UA.aggregate([{"$match": {'user_homepage': homepage}},
                                   {"$project": {"cnt": {"$size": "$user_article"}}}])

    # count => cnt
    # 返回的结果需要转为 list 类型 方可遍历
    res_list = list(res)
    # now_artNum = res_list[0]['cnt']
    now_articleNum = {}
    now_articleNum['now_artNum'] = res_list[0]['cnt']

    return json.dumps(now_articleNum)

# 测试ajax 通信1
# @app.route('/test', methods=['GET', 'POST'])
# def demo_router():
#     message = {}
#     message['key_words'] = 'ok'
#     return json.dumps(message)

# 测试ajax 通信2  window.location.href
# @app.route('/test/show', methods=['GET', 'POST'])
# def demo_router_show():
#
#     return render_template('demo1.html')



# 展示单个用户的爱好
@app.route('/user/show', methods=['GET', 'POST'])
def user_hobby_show():
    # request.form.get('name') => from 表单提取
    homepage = request.form.get('homepage')
    print(homepage)

    # homepage_json = request.get_data()
    # homepage_dict = json.loads(homepage_json)
    # homepage = homepage_dict['homepage']

    # 使用正则验证用户输入的用户主页是否合法
    match_result = re.match(r'(https://)?(www.jianshu.com/u/)?(\w{6}|\w{12})$',
                            homepage)  # \w 匹配数字和大小写字母 例子： https://www.jianshu.com/u/485ed2eb0d8a ?=>出现0 次或多次
    # print(match_result)

    # 发送个前台的信息
    message = {}
    if match_result:    #验证通过
        message['key_words'] = '用户验证通过'
        user_hobby, userInfo = get_userHobby(homepage)
    else:
        message['key_words'] = '输入的用户主页有问题！请重新输入！'
        return json.dumps(message)

    # 各爱好 的名字
    hobby_label = []
    # 各爱好 出现的次数
    hobby_val = []
    # 取前15个出现次数最多的 爱好 及 次数
    if len(user_hobby) < 15:    #用户爱好的个数小于 15时，直接遍历user_hobby
        for hobby in user_hobby:
            for key, val in hobby.items():
                hobby_label.append(key)
                hobby_val.append(val)

    else:
        for hobby in user_hobby[:15]:
            for key, val in hobby.items():
                hobby_label.append(key)
                hobby_val.append(val)

    # 出现爱好次数最多的次数
    max_hobby_val = max(hobby_val) + 5

    # 该用户的常用词与前100篇文章名 形成的词云图
    user_wordcloud = user_wordCloud()
    userCommonWords = user_wordcloud.get_oneUser_commonWords(user_homepage=homepage)
    # print(userCommonWords)

    # 简书用户喜爱书籍 top_books100
    top_video100, top_books100 = user_wordcloud.get_topVideo_Books(user_homepage=homepage)
    print(f"user's top_books100:{top_books100}")
    # ** ，解包思想 合并两个字典
    CommonW_TopBooks = {**userCommonWords, **top_books100}
    # print(CommonW_TopBooks)

    # 取得用户的性别 用以确认使用那张图片进行词云作图
    if userInfo['gender'] == 'woman':
        gender = 'woman.jpg'

    elif userInfo['gender'] == 'man':
        gender = 'man.jpg'

    # 性别为 none的情况
    else:
        gender = 'normal.jpg'

    # 该张图片的绝对路径
    gender_pic = os.path.abspath(curPath + '\\jianshu_huaxiang\\{gender}'.format(gender=gender))

    # 生成词云图片的文件路径及 文件名
    des_picture = os.path.abspath(curPath + '\\static\\img\\{gender}'.format(gender=gender))
    user_wordcloud.user_wordcloud(CommonW_TopBooks, gender_pic, des_picture, 40, 3)

    # render_template('user_huaxiang_show.html', hobby_label=hobby_label, hobby_val=hobby_val,
    #                 max_hobby_val=max_hobby_val, userInfo=userInfo)
    # return json.dumps(message)

    return render_template('user_huaxiang_show.html', hobby_label=hobby_label, hobby_val=hobby_val, max_hobby_val=max_hobby_val, userInfo=userInfo), json.dumps(message)




# 简书群体（女性、男性、未标注性别的 三类人群）的爱好排行榜
@app.route('/crowd', methods=['GET', 'POST'])
def Tophobby():
    return render_template('crowd_huaxiang.html')

@app.route('/crowd/show', methods=['GET', 'POST'])
def Tophobby_show():
    if request.method == 'POST':

        gender = request.form['gender']
        user_num = request.form['user_num']

        # if gender !='' and gender !='man' and gender !='woman':
        #     # 方便提示用户多个错误
        #     # 验证用户输入的人数是否为整数
        #     if not user_num.isdigit():
        #         return render_template('crowd_huaxiang.html', num_error_msg='人数输入有问题！请重新输入！（必须是整数）',
        #         gender_error_msg = '性别输入有问题！请重新输入！（参考信息：留空或输入man或输入woman）')
        #     else:
        #         return render_template('crowd_huaxiang.html', gender_error_msg='性别输入有问题！请重新输入！（参考信息：留空或输入man或输入woman）')
        #
        # # 验证用户输入的人数是否为整数
        # if not user_num.isdigit():
        #     return render_template('crowd_huaxiang.html', num_error_msg='人数输入有问题！请重新输入！（必须是整数）')

        data_info = {}
        data_info['gender'] = gender
        data_info['user_num'] = user_num

    Top_hobby = get_TopHobby(gender=gender, num=int(user_num))

    # 存放爱好的 列表字典
    hobby_list = []

    # 存放爱好的 名字
    hobby_label = []
    # 取前15个出现次数最多的 爱好及次数
    for item in Top_hobby[:20]:
        hobby_dict = {}
        hobby_dict['value'] = item[1]
        hobby_dict['name'] = item[0]
        hobby_list.append(hobby_dict)
        hobby_label.append(item[0])

    return render_template('crowd_huaxiang_show.html', hobby_list=hobby_list, hobby_label=hobby_label, data_info=data_info)


# 数据库里所有的简书用户画像
@app.route('/huaxiang', methods=['GET', 'POST'])
def get_userhuaxiang():
    return render_template('huaxiang.html')


@app.route('/huaxiang/show', methods=['GET', 'POST'])
def userhuaxiang_show():
    if request.method == 'POST':
        user_num = request.form['user_num']
        # 验证用户输入的人数是否为整数
        if not user_num.isdigit():
            return render_template('huaxiang.html', num_error_msg='人数输入有问题！请重新输入！（必须是整数）')

        # 用户所输入 user_num 个用户的爱好（列表套元组）
        hobby_list, W_hobby_list, M_hobby_list = group_huaxiang(num=int(user_num))

        # print(hobby_tup[0])
        # 存放(user_num 个用户)爱好的 列表字典
        alluserhobby_list = []

        # 存放(user_num 个且性别为女性用户)爱好的 列表字典
        woman_hobby_list = []

        # 存放(user_num 个且性别为男性用户)爱好的 列表字典
        man_hobby_list = []

        # 存放爱好的 名字
        hobby_label = []
        # 取前15个出现次数最多的 爱好及次数
        for item in hobby_list[:20]:
            hobby_dict = {}
            hobby_dict['value'] = item[1]
            hobby_dict['name'] = item[0]
            alluserhobby_list.append(hobby_dict)
            hobby_label.append(item[0])

        # 取女性群体前15个出现次数最多的 爱好及次数
        for item in W_hobby_list[:20]:
            hobby_dict = {}
            hobby_dict['value'] = item[1]
            hobby_dict['name'] = item[0]
            woman_hobby_list.append(hobby_dict)

        # 取男性群体前15个出现次数最多的 爱好及次数
        for item in M_hobby_list[:20]:
            hobby_dict = {}
            hobby_dict['value'] = item[1]
            hobby_dict['name'] = item[0]
            man_hobby_list.append(hobby_dict)


    return render_template('huaxiang_show.html', hobby_label=hobby_label, alluserhobby_list=alluserhobby_list,
                           woman_hobby_list=woman_hobby_list, man_hobby_list=man_hobby_list)



if __name__ == '__main__':
    app.run(debug=True)

