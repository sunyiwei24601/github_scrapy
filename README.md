# 利用Github API接口爬取数据

## 基本流程

1. 通过`get_users_details.py`遍历历史的Github Api数据,获取每一个repository的内容和作者,然后保存在total_users中.
2. 分别通过`get_corroborators.py`和`get_followers.py`,获取上述对应的repository的关注者和贡献者,获取具体的贡献量.

## Scrapy的使用

scrapy的本质是一个异步爬取的框架,在命令行中切换到extend文件夹,使用`scrapy crawl contribution_extend`命令进行爬取.

但是Github的API有次数限制,所以注意多账号的切换和秘钥的次数限制,一小时只能调用1000次以内的API.