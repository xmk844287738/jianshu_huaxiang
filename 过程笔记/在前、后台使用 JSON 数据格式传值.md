### 在前、后台使用 JSON 数据格式传值

1. ```html
   一：前台步骤
   
   1. 构建字典对象
   	var dict_object = {'key': 'val',……};
   
   2. 使用 JSON.stringify() 创建 json_object 对象
   	var json_object = JSON.stringify(dict_object);	
   
   3. 使用 ajax 传值
   	$.ajax({
   		url: '路由函数',
   		type: 'POST',
   		data: json_object,
   		dataType: 'json',
   		//前台向后台成功发送数据后的回调函数
   		success: function(datd){
   			//data 为字典对象
   			data.key; //取得某个键值对的值
   	}
   })
   
   
   
   
   ```

   ```python
   二、pyhton后台步骤
   
   1.接收前台穿过来的值
   	json_object = request.get_data()
       
   2.json 字符串对象转为 字典对象
   	dict_object = json.loads(json_object)
       
   3.取得某个键值对的值
   	val = dict_object['key']
       
   4.构建新的字典对象
   	new_dict = {}
       
   5.给new_dict 对象填充值
   	…………
   
   6.给前台返回 json字符串对象
   	return json.dumps(new_dict)
   
   ```

   

### 例子

**前台代码：**

```html
//user.html 

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ajax</title>
</head>
<body>
	<div align="center">
        <div id="" style="margin-top: 150px;">
            <form action="http://localhost:5000/user/show" method="POST">
                <div class="input-group" style="width: 40%;">
                    <input type="text" class="form-control" placeholder="请输入用户的主页..." name="homepage" id="homepage" onblur="func1()">
                    <span class="input-group-btn">
                        <input type="submit" class="btn btn-default" name="op" value="查询">
                    </span>
                </div>
            </form>
        </div>
    </div>
</body>
<script src="../static/js/jquery-3.4.1.min.js" type="text/javascript" charset="utf-8"></script>
	<script type="text/javascript">
    function func1(){
			var homepage = $('#homepage').val();
			// console.log(homepage);
			var dict_object = {
				'homepage':homepage,
			};
			var json_object = JSON.stringify(dict_object);
			$.ajax({
                //路由函数
				url: "/user_homepage",
				type: "POST",
				data:json_object,
				dataType:'json',
				success: function(data) {
					 console.log(data.key_words);
					
					//业务逻辑操作
					if (data.key_words == 'yes'){
						console.log(data.key_words)
					}else{
						console.log(data.key_words);
					}
					
				}
			})
		};
	</script>
</html>



```



二、python后台代码

```python
from flask import Flask, render_template
import json
import re

app = Flask(__name)

#路由函数
@app.router('/user', methods=['GET', 'POST'])
def	user():
    return render_template('user.html')


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

    
if __name__ == '__main__':
    app.run(debug=True)



```

