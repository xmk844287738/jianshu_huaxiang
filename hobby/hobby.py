import pymongo
import os


curPath = os.path.abspath(os.path.dirname(__file__))
# 获取jianshu_flask，也就是项目的根路径
projectPath = curPath[:curPath.find("jianshu_flask\\") + len("jianshu_flask\\")]


# 连接 mongoDB 数据库
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
db = client['jianshu_huaxiang']

# Top100 hobby 集合表
collection_TH = db['commonWords_v3']
# user hobby 集合表
collection_UH_v5 = db['commonWords_v5']


# 简书用户的爱好排行榜
def get_TopHobby(gender, num, skip=0):
    """
    gender 为 None 进行 findall 模式查找  (None 不等于字符串 'none') 返回值：列表套元组
    :param gender: 性别
    :param num: 数据库里前 num 个记录
    :return: 按照各爱好值的按从高到低排序返回一个 各爱好的列表（列表套元组）
    """
    # 载入已准备好用户爱好的大字典
    hobby_str = ''
    # 获取hobby.txt文件的路径 (hobby 文件夹下的hobby.txt)
    hobbyPath = os.path.abspath(projectPath + 'hobby\\hobby.txt')
    with open(hobbyPath, 'r', encoding='utf-8') as f:
        hobby_str = f.read()

    f.close()

    hobby_list = hobby_str.split('\n')
    # 初始化各爱好的次数为0
    hobby_index = [0 for i in range(len(hobby_list))]

    # 以爱好为 key 关键字; 值为 各爱好出现的次数
    hobby_dict = {}
    for x, y in zip(hobby_list, hobby_index):
        hobby_dict[x] = y

    # 读取mongoDb数据库里 前num个用户
    if gender:
        # 规定性别查找
        res = collection_TH.find({'gender': gender}).limit(num).skip(skip)

    else:
        res = collection_TH.find().limit(num).skip(skip)

    for user in res:
        user_hobby = user['user_commonWords'].split(',')
        for hobby in user_hobby:
            if hobby in hobby_list:
                hobby_dict[hobby] += 1

    # 把 hobby_dict 字典按照各爱好值的按从高到低排序
    hobby_list_sort = sorted(hobby_dict.items(), key=lambda hobby_dict: hobby_dict[1], reverse=True)
    users_hobby_list = []
    # 去掉 爱好值为0 的 集合
    for item in hobby_list_sort:
        if item[1] > 0:
            users_hobby_list.append(item)

    return users_hobby_list


# 返回一个用户的爱好字典
def get_userHobby(user_homepage):
    """
    返回一个用户的爱好字典 以爱好名称为key，各爱好出现的次数为 value
    :param user_homepage: 前台传过来的 主页为 user_homepage 的用户
    :return: 返回一个用户爱好字典 以爱好名称为key，各爱好出现的次数为 value
    """
    # 载入已准备好用户爱好的大字典
    hobby_str = ''
    # 获取hobby.txt文件的路径 (hobby 文件夹下的hobby.txt)
    hobbyPath = os.path.abspath(projectPath + 'hobby\\hobby.txt')
    with open(hobbyPath, 'r', encoding='utf-8') as f:
        hobby_str = f.read()

    f.close()

    hobby_list = hobby_str.split('\n')
    # 初始化各爱好的次数为0
    hobby_index = [0 for i in range(len(hobby_list))]

    # 以爱好为 key 关键字; 值为 各爱好出现的次数
    hobby_dict = {}
    for x, y in zip(hobby_list, hobby_index):
        hobby_dict[x] = y

    # 读取mongoDb数据库里 前台传过来的 主页为 user_homepage 的用户
    # 需要进行正则验证！！
    if user_homepage:
        # 规定用户主页查找
        res = collection_UH_v5.find({'user_homepage': user_homepage})

    else:
        return 'error'

    users_hobby_list = []
    for item in res[0]['user_commonWords']:
        for key, value in item.items():
            if key in hobby_list:
                users_hobby_list.append(item)

    # 用户信息
    userInfo = {}
    userInfo['nickname'] = res[0]['nickname']
    userInfo['gender'] = res[0]['gender']

    return users_hobby_list, userInfo



# 简书整体画像比较
# 对用户的爱好进行过滤并排序（去掉爱好值为0的项）
def filter_userHobby(userhobby_dict):
    """
    接收一个字典对象 返回一个过滤后 值不为0的列表套元组对象(hobby_list_filted)
    :param userhobby_dict:
    :return:
    """
    hobby_list_sorted = sorted(userhobby_dict.items(), key=lambda woman_hobby_dict: woman_hobby_dict[1], reverse=True)
    hobby_list_filted = []
    # 去掉 爱好值为0 的 集合
    for item in hobby_list_sorted:
        if item[1] > 0:
            hobby_list_filted.append(item)

    # hobby_list_filted 列表套元组转为字典对象
    hobby_dict_filted = {}
    for item in  hobby_list_filted:
        hobby_dict_filted[item[0]] = item[1]

    # 合并语义相近的键值对
    word_list = [('读', '读书', '朗读'), ('旅行',), ('跑', '锻炼', '跑步'), ('books', 'book', '书')]
    key_word_list = ['阅读', '旅游', '运动', '书籍']
    for i in range(len(key_word_list)):
        # 如果 '阅读'的爱好在 hobby_dict_filted 字典里出现，且元组('读', '读书', '朗读')里的某一元素在 hobby_dict_filted 字典里也出现时;
        if key_word_list[i] in hobby_dict_filted:   #把 ('读', '读书', '朗读') 元组里出现的元素归为一个('阅读')类型
            # 循环元组
            for word in word_list[i]:
                if word in hobby_dict_filted:
                    # 逐次把键为'读', '读书', '朗读'的值叠加到 键为 '阅读' 的值身上
                    hobby_dict_filted[key_word_list[i]] = hobby_dict_filted[key_word_list[i]] + hobby_dict_filted[word]
                    # 把值叠加给 键为 '阅读'的身上后，并删除 hobby_dict_filted（'读', '读书', '朗读'） 对应的键值对
                    del hobby_dict_filted[word]

        else:
            # 循环元组
            for word in word_list[i]:
                # 如果 '阅读'的爱好在 hobby_dict_filted 字典里没有出现，但 元组('读', '读书', '朗读')里的某一元素在 hobby_dict_filted 字典里出现时;
                if word in hobby_dict_filted:
                    # 重新在 hobby_dict_filted字典里 创建 '阅读' = 0 的键值对； 重新开辟空间
                    hobby_dict_filted[key_word_list[i]] = 0
                    break

            # 循环元组
            for word in word_list[i]:
                if word in hobby_dict_filted:
                    # 逐次把键为'读', '读书', '朗读'的值叠加到 键为 '阅读' 的值身上
                    hobby_dict_filted[key_word_list[i]] = hobby_dict_filted[key_word_list[i]] + hobby_dict_filted[word]
                    # 把值叠加给 键为 '阅读'的身上后，并删除 hobby_dict_filted（'读', '读书', '朗读'） 对应的键值对
                    del hobby_dict_filted[word]

    # print(hobby_dict_filted)
    # 合并语义相近的键值对
    # hobby_list_merged = []
    # for item in hobby_dict_filted.items():
    #     hobby_list_merged.append(item)

    # 对 合并语义相近的键值对 hobby_dict_filted 字典对象按照爱好值（升序）重新进行排序
    hobby_list_merged = sorted(hobby_dict_filted.items(), key=lambda hobby_dict_filted: hobby_dict_filted[1], reverse=True)


    # print(hobby_list_merged)

    return hobby_list_merged


def group_huaxiang(num, skip=0):
    """

    :param num:
    :param skip:
    :return:
    """
    # 载入已准备好用户爱好的大字典
    hobby_str = ''
    # 获取hobby.txt文件的路径 (hobby 文件夹下的hobby.txt)
    hobbyPath = os.path.abspath(projectPath + 'hobby\\hobby.txt')
    with open(hobbyPath, 'r', encoding='utf-8') as f:
        hobby_str = f.read()

    f.close()

    hobby_list = hobby_str.split('\n')
    # 初始化各爱好的次数为0
    hobby_index = [0 for i in range(len(hobby_list))]

    # 以爱好为 key 关键字; 值为 各爱好出现的次数
    hobby_dict = {}
    man_hobby_dict = {}
    woman_hobby_dict = {}

    for x, y in zip(hobby_list, hobby_index):
        hobby_dict[x] = y
        # 初始化男性爱好字典
        man_hobby_dict[x] = y
        # 初始化 男性爱好字典
        woman_hobby_dict[x] = y



    # 读取mongoDb数据库里 前num个用户
    res = collection_TH.find().limit(num).skip(skip)

    for user in res:
        # 个数为num所有用户（性别为男、女、none）
        user_hobby = user['user_commonWords'].split(',')
        for hobby in user_hobby:
            if hobby in hobby_list:
                hobby_dict[hobby] += 1

        if user['gender'] == 'woman': #用户为女性
            user_hobby = user['user_commonWords'].split(',')
            for hobby in user_hobby:
                if hobby in hobby_list:
                    woman_hobby_dict[hobby] += 1

        if user['gender'] == 'man': #用户为男性
            user_hobby = user['user_commonWords'].split(',')
            for hobby in user_hobby:
                if hobby in hobby_list:
                    man_hobby_dict[hobby] += 1




    # 过滤并把 woman_hobby_dict 字典按照各爱好值的按从高到低排序
    W_hobby_list= filter_userHobby(woman_hobby_dict)

    # 过滤并把 man_hobby_dict 字典按照各爱好值的按从高到低排序
    M_hobby_list = filter_userHobby(man_hobby_dict)

    # 过滤并把 (user_num 个用户)hobby_dict字典按照各爱好值的按从高到低排序
    userNum_hobby_list = filter_userHobby(hobby_dict)

    return userNum_hobby_list, W_hobby_list, M_hobby_list


if __name__ == '__main__':
    # 抽取数据库里前600个用户
    # 'none' 表示数据库的值;    None 表示真的为空
    users_hobby_list = get_TopHobby(gender=None, num=600, skip=0)
    print(users_hobby_list)
    # print('*' * 60)
    # # 抽取数据库里前600个男性用户
    # Musers_hobby_list = get_TopHobby(gender='man', num=600)
    # print(Musers_hobby_list)
    # print('*' * 60)
    # # 抽取数据库里前600个女性用户
    # Wusers_hobby_list = get_TopHobby(gender='woman', num=600)
    # print(Wusers_hobby_list)

    # 查看某用户的常用词
    # user_commonWords = get_userHobby('https://www.jianshu.com/u/a66dcb0603dd')
    # print(user_commonWords)
