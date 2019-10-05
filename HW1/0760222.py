# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 16:52:08 2019

@author: Corn
"""

import requests
import sys
import re
import time
import traceback
import os
from bs4 import BeautifulSoup

def crawl():
    data_list = []
    popular_list = []
    print("crawl")
    rs = over18()

    for index in range (2324, 2759):
        if index % 10 == 0:
            print (index)
        try:
            url = "https://www.ptt.cc/bbs/Beauty/index{0}.html".format(index)
            req = rs.get(url)
            #print(req.text)
            soup = BeautifulSoup(req.text, 'html.parser')
            #print (soup.div)
            for div in soup.find_all('div', class_='r-ent'):
                date = div.find(class_='date').string
                date = date.replace("/", "").replace(" ","")
                title = div.find('a').get_text()
                like = div.find(class_='nrec').find('span')
    
                if (index == 2324 and date == '1231') or title.find('公告') != -1 :
                    continue
                url = "https://www.ptt.cc" + div.find('a')['href']
                info = (date, title, url)
                data_list.append(info)
                if (like != None and like.string == '爆'):
                    popular_list.append(info)
            time.sleep(0.1)
        except(KeyboardInterrupt):
            exit(0)
        except:
            traceback.print_exc()
        #print (div.find('a').string)
        #print(div.find('a')['href'])
    #print (data_list)
    with open('all_articles.txt', 'w', encoding = 'utf8') as f:
        for line in data_list: 
            data = ','.join(line)
            f.write(data + "\n")
    with open('all_popular.txt', 'w', encoding = 'utf8') as f:
         for line in popular_list: 
             data = ','.join(line)
             f.write(data + "\n")
    #print (popular_list)
    return 
def push(args):
    push_list = []
    push_dict = {}
    boo_dict = {}
    rs = over18()
    start_date = int(args[0])
    end_date = int(args[1])
    if (os.path.exists('all_articles.txt') == False):
        crawl()
    with open('all_articles.txt', 'r', encoding = 'utf8') as f:
        for line in f:
            info = tuple(line.split(','))
            if (int(info[0]) >= start_date and int(info[0]) <= end_date):
                push_list.append(info)
    for article in push_list:
        url = article[2]
        print (url)
        req = rs.get(url[:-1])
        soup = BeautifulSoup(req.text, 'html.parser')
        for div in soup.find_all('div', class_='push'):
            tag = div.find(class_='push-tag').string
            name = div.find(class_='push-userid').string
            #print (tag)
            if tag == "推 ": 
                if name in push_dict:
                    push_dict[name] += 1
                else:
                    push_dict[name] = 1
            if tag == "噓 ": 
                if name in boo_dict:
                    boo_dict[name] += 1
                else:
                    boo_dict[name] = 1
    push = sortedDict(push_dict)
    boo = sortedDict(boo_dict)
    push_num = sum([push[1] for push in push])
    boo_num = sum([boo[1] for boo in boo])
    file_name = 'push[' +  str(start_date) + '-' + str(end_date) + '].txt'
    with open(file_name, 'w', encoding = 'utf8') as f:
        f.write(f'all like: {push_num}\n')
        f.write(f'all boo: {boo_num}\n')
        for i in range(1,11):
            f.write(f'like #{i}: {push[i-1][0]} {push[i-1][1]}\n')
        for i in range(1,11):
            f.write(f'boo #{i}: {boo[i-1][0]} {boo[i-1][1]}\n')
def popular(args):
    popular_list = []
    pic_list = []
    rs = over18()
    start_date = int(args[0])
    end_date = int(args[1])
    if (os.path.exists('all_popular.txt') == False):
        crawl()
    with open('all_popular.txt', 'r', encoding = 'utf8') as f:
        for line in f:
            info = tuple(line.split(','))
            if (int(info[0]) >= start_date and int(info[0]) <= end_date):
                popular_list.append(info)
    for article in popular_list:
        url = article[2]
        print (url)
        req = rs.get(url[:-1])
        soup = BeautifulSoup(req.text, 'html.parser')
        pic_list.extend(dump_url(soup))
    file_name = 'popular[' +  str(start_date) + '-' + str(end_date) + '].txt'
    with open(file_name, 'w', encoding = 'utf8') as f:
        f.write(f'number of popular articles: {len(popular_list)}\n')
        f.writelines('\n'.join(pic_list))
def keyword(args):
    popular_list = []
    pic_list = []
    rs = over18()
    keyword = args[0]
    start_date = int(args[1])
    end_date = int(args[2])
    if (os.path.exists('all_articles.txt') == False):
        crawl()
    with open('all_articles.txt', 'r', encoding = 'utf8') as f:
        for line in f:
            info = tuple(line.split(','))
            if (int(info[0]) >= start_date and int(info[0]) <= end_date):
                popular_list.append(info)
    for article in popular_list:
        url = article[2]
        print (url)
        req = rs.get(url[:-1])
        soup = BeautifulSoup(req.text, 'html.parser')
        main = soup.find(id='main-content').text
        try:
            text = re.findall("[\s\S]*\n\n--\n※ 發",main)[0][:-8]
            if text.find(keyword) != -1:
                article_pic_urls = dump_url(soup)
                if len(args)>= 4 and args[3] == "-d":
                    dump_pic(article_pic_urls, article[1])
                pic_list.extend(article_pic_urls)
        except:
            continue
    #print (f"keyword({keyword})[{start_date}-{end_date}].txt")
    file_name = f"keyword({keyword})[{start_date}-{end_date}].txt"
    with open(file_name, 'w', encoding = 'utf8') as f:
        f.writelines('\n'.join(pic_list))
    
def dump_url(soup):
    #print (soup)
    pic_list = []
    pat = "^(?:https|http)://+[a-zA-Z0-9./]+\.(?:jpg|gif|png)$"
    for urls in soup.find_all('a'):
        if urls.string != None:
            pic_list.extend(re.findall(pat, urls.string))
    return pic_list
def dump_pic(pic_list, title):
    if title[-1] == ' ':
        title = title[:-1]
    my_path = "image"
    my_path = "G:/我的雲端硬碟/照片/DataScience"
    if (os.path.exists('image/') == False):
        os.mkdir(my_path)
    if (os.path.exists(f'{my_path}/{title}') == False):
        os.mkdir(f'{my_path}/{title}')
    pat = '[\w]+\.(?:jpg|gif|png)'
    for pic_url in pic_list:
        filename = re.findall(pat, pic_url)[0]
        if(os.path.exists(f'{my_path}/{title}/{filename}')):
            continue
        r = requests.get(pic_url)
        with open(f'{my_path}/{title}/{filename}', 'wb') as f:
            sys.stderr.write(f"Downloading {filename} from {pic_url}.\n")
            f.write(r.content)
#    if (os.path.exists('image/') == False):
#        os.mkdir('image')
#    if (os.path.exists(f'image/{title}') == False):
#        os.mkdir(f'image/{title}')
#    pat = '[\w]+\.(?:jpg|gif|png)'
#    for pic_url in pic_list:
#        filename = re.findall(pat, pic_url)[0]
#        if(os.path.exists(f'image/{title}/{filename}')):
#            continue
#        r = requests.get(pic_url)
#        with open(f'./image/{title}/{filename}', 'wb') as f:
#            sys.stderr.write(f"Downloading {filename} from {pic_url}.\n")
#            f.write(r.content)   
def over18():
    payload = {
        'from':'/bbs/Beauty/index.html',
        'yes': 'yes'        
    }
    rs = requests.session()
    rs.post("https://www.ptt.cc/ask/over18", data=payload)
    return rs
def sortedDict(dict1): 
    temp = sorted(dict1.items(), key=lambda d: d[0])
    return sorted(temp, key=lambda d: d[1], reverse=True)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "crawl":
            crawl()
        if command == "push":
            push(sys.argv[2:])    
        if command == "popular":
            popular(sys.argv[2:])   
        if command == "keyword":
            keyword(sys.argv[2:])