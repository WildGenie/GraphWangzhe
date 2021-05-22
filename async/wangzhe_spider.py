# -*- coding: utf-8 -*-
# @Time : 2021/5/20 15:38
# @Author : raptor
# @File : wangzhe_spider.py
import json
import os
import time
import mysql.connector as mysql
import requests
from multiprocessing.dummy import Pool
import re

from lxml import etree

'''王者荣耀英雄介绍'''


class AsyncSpider:

    def __init__(self):
        print("初始化。。。。。。")
        self.hero_names = []
        self.hero_img = []
        self.hero_img_prefix = "https://game.gtimg.cn/images/yxzj/img201606/heroimg/"
        self.hero_url = []
        self.hero_url_page_prefix = "https://pvp.qq.com/web201605/herodetail/"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        }
        self.db = mysql.connect(user="root", password="123456", host="localhost", database="spider", port=3306)
        self.cursor = self.db.cursor()
        self.home_url = "https://pvp.qq.com/web201605/herolist.shtml"
        self.hero_url_prefix = "https://pvp.qq.com/web201605/"
        self.hero_page_file_path = "../spiderData/hero_page.json"
        self.hero_name_file_path = "../spiderData/hero.json"

    def get_hero_name(self):
        print("开始获取英雄链接。。。。。。")
        with open('../data/herolist.json', 'r', encoding='utf-8')as fp:
            hero_list_data = json.load(fp)
        for item in hero_list_data:
            self.hero_names.append(item["cname"])
            self.hero_url.append(f'{self.hero_url_page_prefix}{item["ename"]}.shtml')
            self.hero_img.append(f'{self.hero_img_prefix}{item["ename"]}/{item["ename"]}.jpg')
        print("英雄链接获取完成。。。。。。")
        return

    def get_hero_page(self, url):
        print(f"开始解析url={url}")
        response = requests.get(url=url, headers=self.headers)
        response.encoding = "gbk"
        # fp = open('./hero.html', 'w', encoding='gbk')
        # fp.write(response.text)
        with open('../data/ming.json', 'r', encoding='utf-8')as fp:
            ming_data = json.load(fp)
        ming_dict = {}
        for item in ming_data:
            ming_dict[item['ming_id']] = item
        html = etree.HTML(response.text)
        hero_name = html.xpath(".//div[@class='zk-con3 zk-con']/div[@class='crumb']/label/text()")[0]
        hero_skill = html.xpath(
            ".//div[@class='skill-info l info']/div[@class='skill-show']/div[@class='show-list']/p[@class='skill-name']/b/text()")
        hero_skill_detail = html.xpath(
            ".//div[@class='skill-info l info']/div[@class='skill-show']/div[@class='show-list']/p[@class='skill-desc']/text()")
        hero_skill_img = html.xpath(
            ".//div[@class='skill ls fl']/div[@class='skill-info l info']/ul[@class='skill-u1']/li/img/@src")
        hero_ming_id = html.xpath(
            ".//div[@class='zk-con3 zk-con']/div[@class='sugg rs fl']/div[@class='sugg-info info']/ul[@class='sugg-u1']/@data-ming")[
            0].split('|')
        # with open('../data/hero_id.json', 'r', encoding='utf-8')as fp:
        #     hero_id = json.load(fp)

        '''
            前两个  最佳搭档
            中间俩  压制英雄
            后俩   被压制英雄
        '''
        hero_relation_uri = html.xpath(
            ".//div[@class='hero-info-box']/div/div[@class='hero-info l info']/div[@class='hero-list hero-relate-list fl']/ul/li/a/img/@src")
        hero_relation_desc = html.xpath(
            ".//div[@class='zk-con4 zk-con']/div[@class='hero ls fl']/div[@class='hero-info-box']/div/div[@class='hero-info l info']/div[@class='hero-list-desc']/p/text()")
        hero_inscription = []
        for ming_id in hero_ming_id:
            hero_inscription.append(ming_dict[ming_id])
        hero_inscription_tips = html.xpath(
            ".//div[@class='zk-con3 zk-con']/div[@class='sugg rs fl']/div[@class='sugg-info info']/p[@class='sugg-tips']/text()")[
            0]
        hero_recommend_id = html.xpath(
            ".//div[@class='zk-con4 zk-con']/div[@class='equip rs fl']/div[@class='equip-bd']/div[@class='equip-info l']/ul/@data-item")
        hero_recommend_tips = html.xpath(
            ".//div[@class='equip-bd']/div[@class='equip-info l']/p[@class='equip-tips']/text()")
        hero_story = html.xpath("/html/body/div[@id='hero-story']/div[@class='pop-bd']/p/text()")
        # print("名字：", hero_name)
        # print("技能：", hero_skill)
        # print("技能详情：", hero_skill_detail)
        # print("铭文推荐：", hero_inscription)
        # print("铭文推荐Tips：", hero_inscription_tips)
        # print(hero_recommend_id)
        # print(hero_recommend_tips)
        # print(hero_story)

        print(f"解析完成url={url}")
        return hero_name, hero_skill, hero_skill_detail, hero_skill_img, hero_inscription, \
               hero_inscription_tips, hero_relation_uri, hero_relation_desc, hero_recommend_id, hero_recommend_tips, hero_story

    def daili_req(self, url):
        try:
            # 提取代理API接口，获取1个代理IP
            api_url = "http://dps.kdlapi.com/api/getdps/?orderid=902149413591094&num=1&pt=1&sep=1"
            # 获取API接口返回的代理IP
            proxy_ip = requests.get(api_url).text
            print(f'代理ip：{proxy_ip}')
            # 白名单方式（需提前设置白名单）
            proxies = {
                "http": "http://%(proxy)s/" % {"proxy": proxy_ip},
                "https": "http://%(proxy)s/" % {"proxy": proxy_ip}
            }
            print(f"proxies:{proxies}")
            # 使用代理IP发送请求
            response = requests.get(url, headers=self.headers, proxies=proxies)
            # 获取页面内容
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(e.args)

    '''持久化英雄链接信息'''

    def save_hero_name_file(self):
        print("英雄名称及连接写入开始。。。")
        if (os.path.exists(self.hero_name_file_path) == True):
            print(f"{self.hero_name_file_path}已经存在")
            return
        fp = open(self.hero_name_file_path, 'a+', encoding="utf-8")
        for i in range(0, len(self.hero_names)):
            json.dump({
                "name": self.hero_names[i],
                "url": self.hero_url[i],
                "img": self.hero_img[i]
            }, fp=fp, ensure_ascii=False)
            fp.write('\n')
        print("英雄名称及连接写入结束。。。")
        return

    '''持久化英雄详情页'''

    def save_hero_page_file(self, url):
        hero_name, hero_skill, hero_skill_detail, hero_skill_img, hero_inscription, hero_inscription_tips, hero_relation_uri, hero_relation_desc, hero_recommend_id, hero_recommend_tips, hero_story = self.get_hero_page(
            url)
        hero_info = {
            "name": hero_name,
            "skill": hero_skill,
            "skill_detail": hero_skill_detail,
            "skill_img": hero_skill_img,
            "inscription": hero_inscription,
            "inscription_tips": hero_inscription_tips,
            "relation_uri": hero_relation_uri,
            "relation_desc": hero_relation_desc,
            "hero_recommend_id": hero_recommend_id,
            "hero_recommend_tips": hero_recommend_tips,
            "hero_story": hero_story
        }
        print(hero_info)
        self.write_hero_page_file(hero_info)

    def write_hero_page_file(self, data):
        fp = open(self.hero_page_file_path, 'a+', encoding='utf-8')
        json.dump(data, fp=fp, ensure_ascii=False)
        fp.write('\n')

    def start(self):
        start_time = time.time()
        self.get_hero_name()
        self.save_hero_name_file()
        for i in range(0, len(self.hero_url)):
            self.save_hero_page_file(self.hero_url[i])
        # pool = Pool(len(self.hero_names))
        # pool.map(self.get_hero_page, self.hero_url)
        end_time = time.time()
        print(end_time - start_time)

    '''单英雄解析测试'''

    def single(self):
        start_time = time.time()
        # self.get_hero_page("https://pvp.qq.com/web201605/herodetail/518.shtml")
        self.save_hero_page_file("https://pvp.qq.com/web201605/herodetail/518.shtml")
        end_time = time.time()
        print(end_time - start_time)


if __name__ == '__main__':
    spider = AsyncSpider()
    spider.start()
    # spider.single()
