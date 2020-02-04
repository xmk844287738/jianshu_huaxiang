ajax 轮询(Polling)

```javascript
<script>
    function test() {
        $.ajax({
             url: '/new_window_url/',
             async:true,
             type: 'get',
            success: function (data) {
                 var new_url =  $('#new_iframe').attr('src');
                if (new_url !== data){
                     $('#new_iframe').attr('src', data);
                }
             }
        })
     };
	setInterval("test()",500);
</script>
```

setInterval按照固定的周期（单位是毫秒）去执行一个函数或者计算表达式。在Ajax请求里有一个参数非常重要，async为True时代表了是异步请求，这样不会锁死浏览器，但是为False时代表了同步请求会锁住浏览器

 **setInterval在执行完一次代码之后，经过了那个固定的时间间隔，它还会自动重复执行代 码，而setTimeout只执行一次那段代码。**

虽然表面上看来setTimeout只能应用在on-off方式的动作上，不过可以通 过创建一个函数循环重复调用setTimeout，以实现重复的操作：



```javascript
showTime();
function showTime()
{
  var today = new Date();
  alert("The time is: " + today.toString ());
  setTimeout("showTime()", 5000);
}
```



**如果使用setInterval，则相应的代码如下所示：**

```javascript
setInterval ("showTime()", 5000);
function showTime()
{
  var today = new Date();
  alert("The time is: " + today.toString ());
}
```

