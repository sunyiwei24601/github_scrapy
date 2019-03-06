import sys
sys.path.append(sys.path.append("/home/sunyiwei/"))

from Gitrating.connect_tools import *
from Gitrating.tools import *
import json
import requests
from multiprocessing import Process

def get_users_detail(start, end, num):
    with open('users_pointer/users_pointer{num}.json'.format(num=num)) as f:
        n = json.load(f)[0]
        if n < start:
            pass
        else:
            start = n
    url = 'https://api.github.com/users/{login}'
    total_users = []
    with open("total_users.json") as f:
        total_users = json.load(f)
    cursor = get_server_cursor('total_contributors_detail')
    n = start
    for user in total_users[start:end]:
        j = {}
        try:
            r = requests.get(url.format(login=user), headers = get_headers())
            j = json.loads(r.text)
        except:
            pass
        user_detail = {}
        n += 1
        if n % 100 == 0:
            print("this is the {n}th scrapy for process{num}".format(n=n, num =num ))
        if len(j) != 0:
            if not j.get('login'):
                continue
            user_detail['login'] = j['login']
            user_detail['followers'] = j['followers']
            user_detail['public_repos'] = j['public_repos']
            cursor.insert_one(user_detail)
            with open('users_pointer/users_pointer{num}.json'.format(num=num), 'w') as f:
                json.dump([n], f)
    print("process{n} finished".format(n=n))

if __name__ == "__main__":
    p = list()
    p.append(Process(target=get_users_detail, args=(80000, 90000, 1)))
    p.append(Process(target=get_users_detail, args=(90000, 100000, 2)))
    p.append(Process(target=get_users_detail, args=(100000, 110000, 3)))
    p.append(Process(target=get_users_detail, args=(30000, 40000, 4)))
    p.append(Process(target=get_users_detail, args=(110000, 120000, 5)))
    p.append(Process(target=get_users_detail, args=(120000, 130000, 6)))
    p.append(Process(target=get_users_detail, args=(130000, 138153, 7)))
    # p.append(Process(target=get_users_detail, args=(140000, 80000, 8)))
    for process in p:
        process.start()