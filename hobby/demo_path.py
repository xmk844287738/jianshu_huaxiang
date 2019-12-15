

import os
curPath = os.path.abspath(os.path.dirname(__file__))

# 获取jianshu_flask，也就是项目的根路径
# projectPath = curPath[:curPath.find("jianshu_flask\\")+len("jianshu_flask\\")]
# print(projectPath)
# # # 获取video_name.txt文件的路径 (jianshu_huaxiang 文件下的video_name.txt)
# dataPath = os.path.abspath(projectPath + 'jianshu_huaxiang')
# #
# print(dataPath)

# 获取jianshu_flask，也就是项目的根路径
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
print(root_path)