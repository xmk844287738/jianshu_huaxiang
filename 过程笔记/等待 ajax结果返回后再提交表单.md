### 等待 ajax结果返回后 再提交表单

**第一种方法：**

如果使用的提交按钮是button; **不是submit** **以及服务器控件** 可以在ajax返回结果之后document.getElementById('form').submit();	[	jquery写法： $('#表单id).submit()	 **则可以实现 ajax结果返回后再提交表单**]

