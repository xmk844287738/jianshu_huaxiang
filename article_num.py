import requests
from lxml import html

etree = html.etree


def get(url, url_headers):
    try:
        res = requests.get(url=url, headers=url_headers)
        return res
    except:
        get(url, url_headers)

def article_num(user_homepage):
    """
    根据输入的 user_homepage 解析返回用户的文章数量
    :param user_homepage:
    :return:
    """
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


    source = get(user_homepage, index_header)

    # 解析用户的总文章数
    html = etree.HTML(source.content)
    user_article_count = html.xpath('//div[@class="info"]/ul/li/div[@class="meta-block"]/a/p/text()')[2]


    return user_article_count


# if __name__ == '__main__':
#     user_homepage = 'https://www.jianshu.com/u/1bc6a02422f1'
#     article_num = article_num(user_homepage)
#     print(f"user's article num is : {article_num}")