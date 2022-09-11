# -*- coding: utf-8 -*-
# @Time : 2021/5/21 9:38
# @Author : raptor
# @File : GraphHero.py
import os
import json
import mysql.connector as mysql
import requests
from multiprocessing.dummy import Pool

from py2neo import Graph, Node

'''
数据来源：
http://game.gtimg.cn/images/yxzj/act/a20160510story/relavance/data.js
'''

class GraphHero():
    def __init__(self):
        print("GraphHero init...")
        self.hero_roles_path = "../data/hero_roles.txt"
        self.hero_relate_path = "../data/hero_relate.txt"
        self.db = mysql.connect(user="root", password="123456", host="localhost", database="spider", port=3306)
        self.cursor = self.db.cursor()
        self.hero_group = ['河洛', '建木', '逐鹿', '云中漠地', '三分之地', '日落海', '大河流域', '北荒', '东风海域']
        self.g = Graph("http://localhost:7474", username="neo4j", password="123456")
        self.hero_roles = {}
        self.hero_relate = []

    '''读取文件  hero_roles'''

    def read_hero_roles(self):
        print("开始读取人物信息节点     -----       hero_roles.txt")
        for data in open(self.hero_roles_path, "r", encoding='utf-8'):
            data_split = data[1:-3].split(',')
            '''数据录入'''
            # sql = f'insert into hero_roles(hero_name,hero_ename,hero_group,hero_head_pic,hero_story)' \
            #       f' values("{data_split[0]}","{data_split[1]}","{data_split[2]}","{data_split[3]}","{data_split[4]}")'
            # print(sql)
            # self.cursor.execute(sql)
            # self.db.commit()
            self.hero_roles[data_split[0]] = data_split
        # print(self.hero_roles)
        print("读取人物信息节点完成     -----       hero_roles.txt")

    '''读取文件  hero_relate'''

    def read_hero_relate(self):
        print("开始读取人物关系     -----       hero_relate.txt")
        for data in open(self.hero_relate_path, "r", encoding='utf-8'):
            data_split = data[1:-3].split(',')
            '''数据录入'''
            # sql = f'insert into hero_roles(hero_name,hero_ename,hero_group,hero_head_pic,hero_story)' \
            #       f' values("{data_split[0]}","{data_split[1]}","{data_split[2]}","{data_split[3]}","{data_split[4]}")'
            # print(sql)
            # self.cursor.execute(sql)
            # self.db.commit()
            self.hero_relate.append(data_split)
        # print(self.hero_relate)
        print("读取人物关系完成     -----       hero_relate.txt")

    '''建立阵营节点'''

    def create_group_node(self, label, nodes):
        print(f"create_node   label:{label}")
        for node_name in nodes:
            print(f"正在处理  label:{label}  group_name:{node_name}")
            node = Node(label, name=node_name)
            self.g.create(node)
        return

    '''创建阵营节点调用'''

    def create_group_node_process(self):
        print("开始创建阵营。。。")
        self.create_group_node("group", self.hero_group)
        print("创建阵营完成。。。")

    '''创建英雄节点'''

    def create_hero_node(self, label, nodes):
        print(f"create_node   label:{label}")
        for item in nodes:
            print(f"正在处理  label:{label}  hero_name:{item[1]}")
            node = Node(label, hero_ename=item[0], name=item[1], hero_head_pic=item[3], hero_story=item[4])
            self.g.create(node)
        return

    '''创建英雄节点调用'''

    def create_hero_node_process(self):
        hero_roles_temp = [self.hero_roles[item] for item in self.hero_roles]
        print("开始创建英雄。。。")
        self.create_hero_node("hero", hero_roles_temp)
        print("创建英雄完成。。。")

    '''创建英雄阵营关系网'''

    def create_hero_group_relationship(self):
        hero_group_edges = [
            [self.hero_roles[item][1], self.hero_roles[item][2]]
            for item in self.hero_roles
        ]

        # print(hero_group_edges)
        self.create_relationship("hero", "group", hero_group_edges, "阵营", "阵营")

    '''创建实体关联边'''

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        print(
            f"create_relationship start_node:{start_node} end_node:{end_node} edges:{edges} rel_type:{rel_type} rel_name:{rel_name}")
        # 去重处理
        set_edges = ['###'.join(edge) for edge in edges]
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                print(p, rel_type, q)
            except Exception as e:
                print(e)
        return

    '''创建英雄实体关联边'''

    def create_hero_to_hero_relationship_fun(self, start_node, end_node, edges, rel_type, rel_name, loyal, story_map,
                                             desc):
        print(
            f"create_relationship start_node:{start_node} end_node:{end_node} edges:{edges} rel_type:{rel_type} rel_name:{rel_name}")
        p = edges[0]
        q = edges[1]
        query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s',loyal:'%s',story_map:'%s',desc:'%s'}]->(q)" % (
            start_node, end_node, p, q, rel_type, rel_name, loyal, story_map, desc)
        try:
            self.g.run(query)
            print(p, rel_type, q)
        except Exception as e:
            print(e)
        return

    '''英雄关系处理'''

    def create_hero_to_hero_relationship_process(self):
        print("开始处理英雄关系...")
        for item in self.hero_relate:
            self.create_hero_to_hero_relationship_fun("hero", "hero",
                                                      [self.hero_roles[item[0]][1], self.hero_roles[item[1]][1]],
                                                      item[2], item[2], item[3], item[4], item[5])
        # self.create_hero_to_hero_relationship("hero", "hero", , )
        print("处理英雄关系结束...")

    '''构建'''

    def start(self):
        self.read_hero_roles()
        self.create_group_node_process()
        self.create_hero_node_process()
        self.create_hero_group_relationship()
        self.read_hero_relate()
        self.create_hero_to_hero_relationship_process()


if __name__ == '__main__':
    g = GraphHero()
    g.start()
