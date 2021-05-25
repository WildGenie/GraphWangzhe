# -*- coding: utf-8 -*-
# @Time : 2021/5/24 21:58
# @Author : raptor
# @File : GraphHeroSummoner.py
import os
import json
import mysql.connector as mysql
import requests
from multiprocessing.dummy import Pool

from py2neo import Graph, Node


class GraphHeroSummoner():

    def __init__(self):
        print("GraphHeroSummoner init...")
        self.hero_page_path = "../spiderData/hero_page.json"
        self.g = Graph("http://localhost:7474", username="neo4j", password="123456")

    def read_hero_page(self):
        for item in open(self.hero_page_path, encoding='utf-8'):
            data = json.loads(item)
            summoner_ids = data["hero_summoner"][0].split("|")
            for summoner_id in summoner_ids:
                self.create_hero_summoner_relationship("hero", "summoner", [data["name"], summoner_id], "推荐", "召唤师技能推荐")

    '''创建英雄铭文关联边'''

    def create_hero_summoner_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        print(
            f"create_relationship start_node:{start_node} end_node:{end_node} edges:{edges} rel_type:{rel_type} rel_name:{rel_name}")
        p = edges[0]
        q = edges[1]
        query = "match(p:%s),(q:%s) where p.name='%s'and q.summoner_id=%s create (p)-[rel:%s{name:'%s'}]->(q)" % (
            start_node, end_node, p, q, rel_type, rel_name)
        try:
            self.g.run(query)
            print(p, rel_type, q)
        except Exception as e:
            print(e)
        return

    def start(self):
        self.read_hero_page()


if __name__ == '__main__':
    g = GraphHeroSummoner()
    g.start()
