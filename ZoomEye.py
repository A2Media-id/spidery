#!/usr/bin/python
# coding:utf-8
import pickle

import requests
from bs4 import BeautifulSoup
import json
import re


def main():
    invalids=[
        ('260@qq.com', '260@qq.com'),
        ('1123302584@qq.com', 'taoqi512512'),
        ('623257096@qq.com', 'cS10241024'),
        ('499744187@qq.com', 'zhangfei66217985'),
    ]
    auths = [
        ('testerlyx@foxmail.com', '-TesterCC07-'),
        ('280298985@qq.com', 'wcf@1219'),
        # ('623257096@qq.com', 'cS10241024'),
        # ('499744187@qq.com', 'zhangfei66217985'),
        ('hatboy-dj@qq.com', '7r^3&bfswX^K6g85'),
        ('2382614177@qq.com', 'cgs110110'),
        ('979784643@qq.com', 'FKP19960317'),
        ('1147121947@qq.com', 'wjlO0OO0OOO0'),
        ('157303749@qq.com', 'mypasswordisnull12312'),

        ('3214436480@qq.com', 'aa15074520721'),
        ('907937976@qq.com', 'bupt1210'),
        ('youngcraft@qq.com', 'cnxc2008ymgk'),
    ]
    works=[]
    for x in auths:
        u, p = x
        data = {'username': u, 'password': p}
        login = requests.post('https://api.zoomeye.org/user/login', json=data)
        print(u, login.json())
        if login and (login.json() and login.json().get('access_token')):
            works.append(x)

    exit()
    headers = {
        "Authorization": "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6IjIwNzI2MjI5ODlAcXEuY29tIiwiaWF0IjoxNTkzNTkyNDM2LCJuYmYiOjE1OTM1OTI0MzYsImV4cCI6MTU5MzYzNTYzNn0.4EkTH3vh3JSjBJ_wEfnaMhQWuPSaIzQypBAKpfUSuZ0"
    }
    url = "https://api.zoomeye.org/host/search?query=port:6379"
    info = requests.get(url=url, headers=headers)
    info = requests.get(url=url, headers=headers)

    r_decoded = json.loads(info.text)
    print(r_decoded)
    for line in r_decoded['matches']:
        print(line['ip'] + ': ' + str(line['portinfo']['port']))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupted by user, killing all threads...")
