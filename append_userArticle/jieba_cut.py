import jieba
import pandas as pd
from collections import Counter
import os



def articles_common_words(article_content, top_words):


    # curPath = os.path.abspath(os.path.dirname(__file__))
    # stopwords_txt = os.path.abspath(curPath + '\\append_userArticle\\stopwords.txt')

    stopwords = pd.read_csv('stopwords.txt', encoding='utf8', names=['stopword'], index_col=False)

    # stopword_lsit 停用词列表
    stopword_lsit = stopwords['stopword'].tolist()
    '''  article_content => 字符串类型, top_words => int整型,  返回值 top_word_list 列表类型 是一篇文章的常用词 '''
    x = list(jieba.cut(article_content))

    # 存放过滤后的词
    y = []
    for i in x:
        if i not in stopword_lsit:
            y.append(i)

    counter = Counter(y)
    list_words = counter.most_common()

    lst2 = list(filter(lambda x: x[0] != '\n' and x[0] != ' ' and x[0] != ',' and x[0] != ' ', list_words))

    # print(lst2[:top_words])
    top_word_list = lst2[:top_words]
    return top_word_list


if __name__ == '__main__':
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        temp = f.read()

    f.close()
    print(temp)