import json
import time
import requests
import traceback
from multiprocessing import Process
import os
import sys

sys.path.append("/home/sunyiwei/")
import logging
from Gitrating.tools import *
from Gitrating.connect_tools import *

#获取数据库中的repo数据集,形成一个函数方便进行多进程处理操作

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)  # 设置基本level
#这里需要注意一点，基础level要设置比较低一些，后面handler设置的level只有比基础高才有效。

# 输出到控制台，不设置format
handler_stream = logging.StreamHandler(sys.stdout)
handler_stream.setLevel(level=logging.WARN)  # 更改level
logger.addHandler(handler_stream)

# 输出到文件，继承基础level
handler_file = logging.FileHandler('my.log')
formatter = logging.Formatter('%(asctime)s  %(message)s')
handler_file.setFormatter(formatter)  # 设置format
logger.addHandler(handler_file)


def get_contributors_process(start, step, num, language):
    #首先呢，读取存储的位置，如果小于start就用start，如果大于start就用存储的，如果大于end，就直接返回爬虫结束。
    if os.path.exists("contributor_pointer{}.json".format(num)):
        with open("contributor_pointer{}.json".format(num)) as f:
            past_node = json.load(f)[0]
            if past_node > start + step:
                print("Process{} is finished.".format(num))
                return
            if past_node > start:
                start = past_node
    cursor = get_server_cursor('repository_total_detail')
    end = start + step
    print("Process{num} cursor标记完毕".format(num=num))
    
    #通过pages_tool一步到位获取所有的内容
    n = start
    success_count = 0
    #用以记录到了哪里
    
    for ii in range(1, 100):
        if n > end:
            break
        repos = cursor.find().skip(n).limit(2000)
        for rep in repos:
            
            #标记准确率，方便查看
            if n % 500 == 0:
                success_rate = success_count / 500
                prompt = "The {n}th finding for process {num} is {rate}".format(n=n, num=num,
                                                                                rate=success_rate), time.ctime()
                print(prompt)
                logger.info(prompt)
                with open('contributor_pointer{}.json'.format(num), 'w') as f:
                    json.dump([n], f)
                success_count = 0
            
            try:
                idd = rep['id']
                login = rep['owner']['login']
                name = rep['name']
                url = 'https://api.github.com/repos/{owner}/{repos}/stargazers'.format(owner=login, repos=name)
                if rep.get('primaryLanguage'):
                    primary_language = rep['primaryLanguage'].get('name')
                    
                    if primary_language == language:
                        n += 1
                    
                    else:
                        n += 1
                        continue
                else:
                    n += 1
                    continue
                
                n += 1
                
                try:
                    followers = list(followers_tool(url))
                    if len(followers) >= 1:
                        if len(followers[0]) >= 1:
                            success_count += 1
                            # print(followers[0][0])
                
                except requests.exceptions.ConnectionError as e:
                    up = cursor.update_one({'id': idd}, {"$set": {'followers': [[]]}})
                    continue
                except:
                    traceback.print_exc()
                    logger.info('There are something wrong for Process{num}'.format(num=num), exc_info=True)
                    continue
                #根据id来标记rep并更改
                up = cursor.update_one({'id': idd}, {"$set": {'followers': followers}})
            except:
                traceback.print_exc()
                logger.info('There are something wrong for Process{num}'.format(num=num), exc_info=True)
                continue
            #此处应该加入一个审核结果是否正确的函数


if __name__ == "__main__":
    p = list()
    language = "Ruby"
    p.append(Process(target=get_contributors_process, args=(100, 100000, 1, language)))  #18150
    p.append(Process(target=get_contributors_process, args=(100000, 100000, 2, language)))  #11500
    p.append(Process(target=get_contributors_process, args=(200000, 100000, 3, language)))
    p.append(Process(target=get_contributors_process, args=(300000, 100000, 4, language)))  #
    p.append(Process(target=get_contributors_process, args=(400000, 100000, 5, language)))  #
    p.append(Process(target=get_contributors_process, args=(500000, 100000, 6, language)))  #
    p.append(Process(target=get_contributors_process, args=(600000, 100000, 7, language)))  #
    p.append(Process(target=get_contributors_process, args=(700000, 100000, 8, language)))
    # p.append(Process(target=get_contributors_process, args=(2960000, 100000, 9, language)))
    # p.append(Process(target=get_contributors_process, args=(3060000, 100000, 10, language)))
    # p.append(Process(target=get_contributors_process, args=(3160000, 100000, 11, language)))
    #106-216 million for Ruby 10/28 00:31
    #216-326 million for Ruby 10/31 00:58
    
    for process in p:
        process.start()
