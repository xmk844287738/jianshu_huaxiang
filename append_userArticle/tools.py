import re
import chardet


class DecodingUtil(object):
    """解码工具类"""

    # 使用 @ staticmethod或 @ classmethod，就可以不需要实例化，直接类名.方法名()来调用。
    @staticmethod
    def decode(content):
        """
        读取字节数据判断其编码，并正确解码
        :param content: 传入的字节数据
        :return: 正确解码后的数据
        """
        print(chardet.detect(content))
        the_encoding = chardet.detect(content)['encoding']
        try:
            # temp = content.decode(the_encoding)
            # print(temp)
            if not the_encoding:
                return content.decode(the_encoding)
            else:
                return content.decode('utf-8')
        except UnicodeDecodeError:
            print('解码Error!')
            try:
                print('解码测试成功')
                return content.decode('utf-8')
            except:
                return '未能成功解码的文章内容！'

        finally:
            return content.decode('utf-8')


def rep_invalid_char(old:str):
    """mysql插入操作时，有无效字符，替换"""
    invalid_char_re = r"[/?\\[\]*:＊]"
    return re.sub(invalid_char_re, "_", old)