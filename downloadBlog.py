#!/usr/bin/env python
# coding: utf-8
import re

from bs4 import BeautifulSoup as bs, BeautifulSoup
import requests
import urllib.request
import os
import io
import sys
import warnings

warnings.filterwarnings("ignore")
css_content = """
<link href="https://cdn.hinatazaka46.com/files/14/hinata/product/css/sph20201212.css" rel="stylesheet" />
<style>
body{ padding: 20px; }
</style>
"""

title_date = """
<div class="c-blog-article__title">
    {}
</div>
<div class="p-blog-article__info">
    <div class="c-blog-article__date">
        {}
    </div>
</div>
"""
base_directory = "./BLOG/SAKURAZAKA46"
base_url = "https://sakurazaka46.com"

#

member_name = {"上村莉菜": "Rina Uemura", "小池美波": "Minami Koike", "齋藤冬優花": "Fuyuka Saito",
               "井上梨名": "Rina Inoue", "遠藤光莉": "Hikari Endo", "大園玲": "Rei Ozono",
               "大沼晶保": "Akiho Onuma", "幸阪茉里乃": "Marino Kosaka", "武元唯衣": "Yui Takemoto",
               "田村保乃": "Hono Tamura", "藤吉夏鈴": "Karin Fujiyoshi", "増本綺良": "Kira Masumoto",
               "松田里奈": "Rina Matsuda", "森田光": "Hikaru Morita", "守屋麗奈": "Rena Moriya",
               "山﨑天": "Ten Yamazaki", "石森璃花": "Rika Ishimori", "遠藤理子": "Riko Endo",
               "小田倉麗奈": "Rena Odakura", "小島凪紗": "Nagisa Kojima", "谷口愛季": "Aiki Taniguchi",
               "中嶋優月": "Yuzuki Nakajima", "的野美青": "Mio Matono", "向井純葉": "Itoha Mukai",
               "村井優": "Yu Murai", "村山美羽": "Miu Murayama", "山下瞳月": "Shizuki Yamashita"}


def get_html(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0')
    response = urllib.request.urlopen(req)
    html = response.read()
    return html


def downloadImg(article, name, saveDir, date):
    # print(article)
    html = article.prettify()
    html = html.replace('</img>', ' ')
    html = fix_html(html)
    article = BeautifulSoup(html, 'html.parser')
    img_list = article.findAll('img')
    for img in img_list:
        print(img)
        print(img['src'])


    for i, img in enumerate(img_list):
        src = img['src']
        print("i:" + str(i) + "src:" + src)
        filename = date + " " + str(member_name[name]) + "_" + str(i)
        # 负责更改原html的img src的内容 s:<img src="0.jpg">
        s = "<" + "img src=" + '"' + filename + '.' + src.split('.')[-1] + '"' + ">"
        # s = "<" + "img src=" + '"' + str(i) + '.jpg"' + ">"
        img_list[i].replace_with(s)


        # if src != '':
        #     try:
        #         tmp = requests.get(base_url+src)
        #         # with open(saveDir + str(i) + '.jpg', 'wb') as f:
        #         with open(saveDir + filename + '.' + src.split('.')[-1], 'wb') as f:
        #             f.write(tmp.content)
        #     except requests.exceptions.InvalidSchema:
        #         continue

    return article


def fix_html(article_html):
    # 用正则表达式将不完整的img标签闭合
    fixed_html = re.sub(r'<img\s+[^>]*?>', r'\g<0></img>', article_html)
    return fixed_html


def saveHtml(article, saveDir, blogTime, title):
    with open(saveDir + blogTime.replace(":", "-") + ".html", mode='w', encoding='utf-8') as f:
        strHTML = str(article)
        html = strHTML.replace('&lt;', '<').replace('&gt;', '>')

        date = blogTime
        top_content = title_date.format(title, date)
        f.write(css_content)
        f.write(top_content)
        f.write("""<div class="c-blog-article__text">""")
        f.write(html)
        f.write("""</div>""")
        print(blogTime + " save complete!!")
    return


def get_title(soup):
    # 查找指定元素
    h1_title = soup.find('h1', class_='title')

    # 提取文字部分
    if h1_title:
        title = h1_title.get_text()

    div_foot = soup.find(class_='blog-foot')
    div_date = div_foot.find('p', class_='date wf-a')
    if div_date:
        date = div_date.text.replace("/", ".")
    return title, date


def startDownload(name, page, req_bs):
    # 创建目录
    path = os.path.join(base_directory, name)
    os.makedirs(path, exist_ok=True)

    print("新目录的路径是:", path)

    ct = str(member[name])

    url_list = getBlogUrl(req_bs)

    for url in url_list:
        html = get_html(url)
        req_bs = bs(html)

        # article = req_bs.find(class_="box-article")

        soup = BeautifulSoup(html, 'html.parser')
        article = soup.find(class_="box-article")

        title, date = get_title(req_bs)
        blogTime = date

        illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in illegal_chars:
            title = title.replace(char, '_')
        if len(title) > 130:
            subtitle = title[:130]
        else:
            subtitle=title

        date_ = blogTime.replace(":", "-")
        saveDir = os.path.join(path, date_ + " " + subtitle + "/")
        if not os.path.isdir(saveDir):
            if not os.path.isdir(saveDir):
                os.makedirs(saveDir)
            article = downloadImg(article, name, saveDir,date_)

            flag = "OK"
        else:
            flag = "EXIST"
            print(blogTime + " already exists!")
        if flag == "OK":
            print("test")
            print(article)
            saveHtml(article, saveDir, blogTime, title)
            # print("test")


def getBlogUrl(req_bs):
    url_list = []

    # 找到目标<ul>标签
    target_ul = req_bs.find('ul', class_='com-blog-part box3 fxpc')

    # 如果找到了目标<ul>标签
    if target_ul:
        # 找到<ul>标签内的所有超链接
        links = target_ul.find_all('a', href=True)
        # 存储所有超链接
        for link in links:
            blog_url = "https://sakurazaka46.com" + link['href']
            # print("获取blog 链接:"+blog_url)
            url_list.append(blog_url)

    return url_list


member = {"上村莉菜": "03", "小池美波": "06", "齋藤冬優花": "08", "井上梨名": "43", "遠藤光莉": "53", "大園玲": "54",
          "大沼晶保": "55", "幸阪茉里乃": "56", "武元唯衣": "45", "田村保乃": "46", "藤吉夏鈴": "47", "増本綺良": "57",
          "松田里奈": "48", "森田光": "50", "守屋麗奈": "58", "山﨑天": "51", "石森璃花": "59", "遠藤理子": "60",
          "小田倉麗奈": "61", "小島凪紗": "62", "谷口愛季": "63", "中嶋優月": "64", "的野美青": "65", "向井純葉": "66",
          "村井優": "67", "村山美羽": "68", "山下瞳月": "69"}

if __name__ == "__main__":

    print('请注意 不要随便中断下载')
    print('如果重新下载请删除掉原来未下载完的文件夹以避免文件缺失')
    print('输入时 成员名字为日文原名')
    name = input('請輸入要下載的成員(一次輸入一個成員)：')
    # start_page = int(input("请输入你想开始的页数: "))
    # end_page = int(input("请输入你想结束的页数: "))
    print("网站默认页数从0开始 请注意")
    page = 0
    hasPage = True
    while (hasPage != False):
        # 构建完整的URL
        url = "https://sakurazaka46.com/s/s46/diary/blog/list?ima=0000&page=" + str(page) + "&ct=" + str(member[name])
        print("Get: " + url)
        html = get_html(url)
        req_bs = bs(html)
        url = req_bs.find('ul', class_='com-blog-part box3 fxpc')

        if url is None:
            print("All page is downloaded!")
            hasPage = False
            break
        else:
            startDownload(name, page, req_bs)

        page += 1
