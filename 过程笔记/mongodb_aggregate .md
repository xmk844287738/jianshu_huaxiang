###    MongoDB aggregate 聚合操作 获取数组字段的长度

   

   

```sql
   统计 site 集合里 user_article (arrayfield 数组字段)的长度
   mongoDB shell 操作
 db.getCollection('site').aggregate([{ "$match" : { 'user_homepage': 'https://www.jianshu.com/u/f4b235710e5d'}}, { "$project" : {"cnt":{"$size":"$user_article"} }} ])
   
   
   
```

   ```python
#  统计 site 集合里 user_article (arrayfield 数组字段)的长度
# python 下操作

res = collection_UA.aggregate([{"$match": {'user_homepage': 'https://www.jianshu.com/u/3085ce78c719'}}, {"$project": {"cnt": {"$size":"$user_article"}}}])

#返回的结果需要转为 list 类型 方可遍历
res_list = list(res)
res_list[0]['cnt'] #得到 user_article 的长度值

   ```