# -*- coding: utf-8 -*-
import sys
import time
import json
import scrapy
from scrapy import Request
import re
import requests
from lxml import etree

S = 'issues_detail'
sys.path.append(r'C:\Users\Carl\PycharmProjects')

from Gitrating.connect_tools import *


def count_contributions(u):
    
    w = u['weeks']
    num_a = 0
    num_d = 0
    num_c = 0
    for i in w:
        num_a += i['a']
        num_d += i['d']
        num_c += i['c']
    return {'add': num_a,
            'del': num_d,
            'com': num_c,
            }


def find_user(a, name):
    for i in a:
        if i['author']['login'] == name:
            return i
    
    return {'weeks': []}


class ContributionExtendSpider(scrapy.Spider):
    #设置代理地址
    ips = []
    scrapy_time_a = time.time()
    handle_httpstatus_list = [404, 429]

    #想要在初始化过程中使用class 的内置函数，只能用这个方法
    #这说明在class的创建过程中，变量》函数》执行__init__
    def __init__(self):
        # self.refresh_proxies()
        pass
    
    #代理刷新函数
    def refresh_proxies(self):
        url = 'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=fcf96da5e8714181ab262e069a561d60' \
              '&count=5&expiryDate=0&format=1&newLine=2'
        s = requests.get(url)
        print(s.text)
        t = s.text
        j = json.loads(t)
        self.ips = []
        for i in j['msg']:
            self.ips.append(i['ip']+':'+i['port'])

    cursor = get_cursor('sss')
    repos = cursor.find()
    names = []
    for rep in repos:
        if not rep.get('disappear'):
            if rep.get('new_contributions'):
                if not rep.get('contribution_line'):
                    names.append(rep.get('full_name', None))
                    print(rep.get('full_name'))
    print(len(names), "还有这么多大佬有问题")
    name = 'contribution_extend'
    allowed_domains = ['github.com']
    start_urls = ['http://github.com/']
    contributors_url = 'https://github.com/{nm}/graphs/contributors-data'
    code_frequency_url = 'https://github.com/{nm}/graphs/code-frequency-data'
    issues_url = 'https://github.com/{nm}/issues'
    headers = {
        'User-Agent'      :'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Accept'          :'text/html,application/json',
        # 'Cookie'         : '_ga=GA1.2.1415588079.1525289744; _octo=GH1.1.388384250.1525289744; user_session=H2h7q6Syt-X4cKiuB-odGoo5JwwQnPrHYmPrHV6obZAEyECB; __Host-user_session_same_site=H2h7q6Syt-X4cKiuB-odGoo5JwwQnPrHYmPrHV6obZAEyECB; logged_in=yes; dotcom_user=sunyiwei24601; has_recent_activity=1; tz=Asia%2FShanghai; _gat=1; _gh_sess=NWxMU1daVU50ejN4TG9UT0JMWGE0Y3BiQ2RrYldXY1ZTWDBaYnlSemhkNDV2Wmg3eGs1bUFJSjRTU2JVZ3NGckJpSlQ0ODh1YjdIQjl6dS9hZGlYUkxON25OdW5BallkLzA4UGRzbGMrWTVJNzJSK1h4YTQ3eXlqb0JyOEswaHRFdGxrQWo2U0NESFAxWEpHMzJmT1VLSFh6Wkhpc1dsREdGQlBGNWMrd0h2dkVvN3VWQ0x1aDd3ZmxMN2wrNDR5bTdRN2RDZTZxZ1hHdU90aE11dEJpQkxQcXRZYnhGYVBwQjVUOWcxeFByYXh5K0lCbCtFbGFEY3l5SWVRclhCYkFWczZTZ3RQWitWc3EzcnkwNGZTS1E9PS0tWGh6UW9nNmpGVHJmVENGVm5ZUk5tUT09--c9add1697f7ed767122e88c8919abb4b869d7baa',
        'Connection'      : 'keep-alive',
        #'Accept-Language': 'zh-CN,zh;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    
    
    def start_requests(self):
        start = 3620
        end = 0
        for nm in self.names[0:]:
            contri_url = self.contributors_url.format(nm=nm)
            code_url = self.code_frequency_url.format(nm=nm)
            issues_url = self.issues_url.format(nm=nm)
            r = Request(url=contri_url, headers=self.headers, meta={'name': nm}, callback=self.contri_parse)
            yield r
            # r = Request(url=code_url, headers=self.headers, meta={'name': nm}, callback=self.code_parse)
            # yield r
            # r = Request(url=issues_url, headers=self.headers, meta={'name': nm}, callback=self.issues_parse)
            # yield r
    
    def contri_parse(self, response):
        print(response.status, end="  ")
        status = response.status
        if status == 404:
            my_query = {'full_name': response.meta['name']}
            new_values = {'$set': {'disappear': 1}}
            self.cursor.update(my_query, new_values)
            print()
            
        if status == 429:
            time.sleep(60)
            
        if status == 200:
        
            r = response.text
            try:
                j = json.loads(r)
            except:
                print(j)
                print(response.url)
                return 0
                
            contributors = self.cursor.find_one({'full_name': response.meta['name']}).get('contributors',[])
            cons = []  #所有contributors放到同一个list里面，重新搭配
            for contributs in contributors:
                cons += contributs
            for contributor in cons:
                name = contributor['login']
                try:
                    
                    s = find_user(j, name)
                    contributions = count_contributions(s)
                    contributor['contributions_lines'] = contributions
                except:
                    print(j)
                    break
                    
                #挨个找到contributors，然后计算他的代码提交数量
                
                
            #在mongodb中更新
            
            my_query = {'full_name': response.meta['name']}
            new_values = {'$set': {'new_contributions': cons}}
            self.cursor.update(my_query, new_values)
            print(response.meta['name'])
        else:
            print(response.meta['name'])
        
    def code_parse(self, response):
        r = response.text
        try:
            rep_name = response.meta['name']
            j = json.loads(r)
            my_query = {'full_name': rep_name}
            new_values = {'$set': {'code_frequency': j}}
            self.cursor.update(my_query, new_values)
        except:
            print(response)
            print(response.url)
            print('code_error!!!', r)
          
    def issues_parse(self, response):
        r = response.text
        # print(r[:10])
        selector = etree.HTML(r)
        rep_name = response.meta['name']
        # 寻找open和closed的内容，并提取
        try:
            open_content = selector.xpath('//*[@id="js-issues-toolbar"]/div/div[1]/a[1]/text()')[1].strip()
            closed_content = selector.xpath('//*[@id="js-issues-toolbar"]/div/div[1]/a[2]/text()')[1].strip()
            open_issues = int(re.findall('([0-9]+) Open', open_content)[0])
            closed_issues = int(re.findall('([0-9]+) Closed', closed_content)[0])
            issues_detail = [open_issues, closed_issues]
        except:
            print(response)
            print(response.url)
            issues_detail = [0, 0]
        # 更新到mongodb
        
        print(issues_detail)
        my_query = {'full_name': rep_name}
        new_values = {'$set': {'issues_detail': issues_detail}}
        self.cursor.update(my_query, new_values)


if __name__ == "__main__":
    cursor = get_cursor('sss')
    repos = cursor.find()
    names = []
    for rep in repos:
        if  rep.get('new_contributions', '1') == '1':
            names.append(rep)
    for i in names:
        print(i['full_name'])