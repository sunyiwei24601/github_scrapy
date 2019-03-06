# -*- coding: utf-8 -*-
import scrapy
import sys
import random
import time
import json
import threading
from scrapy import Request
import re
import requests
import traceback
from lxml import etree
from threading import local

S = 'issues_detail'
sys.path.append(r'/home/ywsun/')
# from Github_rating.tools import *
# from Github_rating.connect_tools import *

from Gitrating.connect_tools import *
from Gitrating.tools import *


def get_headers():
    tokens = [
        # '9a9c1d46c47f75f57aa382d76b0b0ed98b71ffcc',
        'd6cd802b17e4382c1bcea961e1f6cd4ee0fa8a35',
        '37778db34015b99bdb6ba164e93ef7f105fac4cc',
    ]
    headers = {
        'Authorization': 'token ' + random.choice(tokens),
        'Accept':        'application/vnd.github.v3.star+json,'
                         'application/vnd.github.symmetra-preview+json,'
                         'application/vnd.github.squirrel-girl-preview,'
                         'application/vnd.github.hellcat-preview+json,'
                         'application/vnd.github.mercy-preview+json,'
        
    }
    return headers



local_school = local()

def check_finished(rep):
    check_list = ['events_count', 'subscribers_count', 'commits_count', 'comments_count',
                  'issue_comments_count', 'issues_count']
    for index in check_list:
        if not rep.get(index):
            return False
    return True


class get_num_Thread(threading.Thread):
    def __init__(self, url, reps, index, name, cursor, time_a):
        threading.Thread.__init__(self)
        self.url = url
        self.reps = reps
        self.index = index
        self.name = name
        self.cursor = cursor
        self.time_a = time_a
    def run(self):
        
        try:
            num = self.get_page_nums(self.url)
        except:
            num = 0
            traceback.print_exc()
        rep = self.reps[self.index]
        rep[self.name] = num
        
        if check_finished(rep):
            self.cursor.insert(rep)
            time_b = time.time()
            print(self.url, time.ctime(time_b), time_b - self.time_a)
            self.reps.pop(self.index)

    def get_page_nums(self, url):
        try:
            local_school.response = requests.get(url, headers=get_headers())
        except:
            print('*******response error******')
            traceback.print_exc()
        headers = local_school.response.headers
    
        link = headers.get('Link')
    
        page_num = page_preview(link)
        n = (page_num - 1) * 30
        last_url = url + '?page=' + str(page_num)
        #print(last_url,end=' ')
        try:
            local_school.j = get_tools(last_url)
        except:
            print('*******connect error******')
            traceback.print_exc()
    
        if random.random() < 0.025:
            try:
                print(local_school.j[0])
            except:
                print('error j print')
        n = n + len(local_school.j)
        # print('计算出数量', n)
        return n
            

class FeatureSpider(scrapy.Spider):
    name = 'feature'
    allowed_domains = ['api.github.com']
    cursor = get_server_cursor('members')
    i_cursor = get_server_cursor('selected_members')
    members = list(cursor.find().skip(32000).limit(10))
    repos = []
    current_repos = {}
    def start_requests(self):
        n = 0
        
        for member in self.members:
            print(n)
            n += 1
            member['reps'] = []
            member.pop('_id')
            self.i_cursor.insert_one(member)
            if not member.get('update'):
                for reps in member.get('repos'):
                    for rep in reps:
                        if isinstance(rep, dict):
                            if (rep['stargazers_count'] or rep['watchers_count']
                                    or rep['forks']):
                                self.current_repos[rep['full_name']] = rep
                                events_url = rep['events_url'].split('{')[0]
                                subscribers_url = rep['subscribers_url'].split('{')[0]
                                commits_url = rep['commits_url'].split('{')[0]
                                comments_url = rep['comments_url'].split('{')[0]
                                issue_comments_url = rep['issue_comment_url'].split('{')[0]
                                issues_url = rep['issues_url'].split('{')[0]
                                url_list = [events_url, subscribers_url, commits_url, comments_url, issue_comments_url,
                                            issues_url]
                                check_list = ['events_count', 'subscribers_count', 'commits_count', 'comments_count',
                                              'issue_comments_count', 'issues_count']
                                for i in range(6):
                                    r = Request(url=url_list[i], headers=get_headers(),
                                                meta={'login': rep['owner']['login'], 'name': check_list[i],
                                                      'full_name': rep['full_name']},
                                                callback=self.parse)
                                    yield r
                # self.cursor.update_many({'id': member['id']}, {'$set': {'update': True}})
    
    def parse(self, response):
        a = time.time()
        login = response.meta['login']
        name = response.meta['name']
        full_name = response.meta['full_name']
        headers = response.headers

        link = headers.get('Link')
        try:
            link = link.decode('utf-8')
        except:
            pass
        page_num = page_preview(link)
        n = (page_num - 1) * 30
        last_url = response.url + '?page=' + str(page_num)
        #print(last_url,end=' ')
        try:
            j = get_tools(last_url)
        except:
            print('*******connect error******')
        if random.random() < 0.025:
            try:
                print(j[0])
            except:
                print("print 0th error")
                pass
        n = n + len(j)
        #print(n)
        self.current_repos[full_name][name] = n
        if check_finished(self.current_repos[full_name]):
            self.i_cursor.update({'login': login}, {'$push': {'reps': self.current_repos[login]}})
        
        
        
        
        
        # rep['events_count'] = get_page_num(events_url)
        # rep['subscribers_count'] = get_page_num(subscribers_url)
        # rep['commits_count'] = get_page_num(commits_url)
        # rep['comments_count'] = get_page_num(comments_url)
        # rep['issue_comments_count'] = get_page_num(issue_comments_url)
        # rep['issues_count'] = get_page_num(issues_url)
        
        # b = time.time()
    
        # print(rep['events_url'], time.asctime(time.localtime(time.time())), print(b-a))
        # self.i_cursor.update({'login': login}, {'$push': {'reps': rep}})
