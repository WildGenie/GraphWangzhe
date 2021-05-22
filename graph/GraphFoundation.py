# -*- coding: utf-8 -*-
# @Time : 2021/5/22 18:15
# @Author : raptor
# @File : GraphFoundation.py
import os
import json
from py2neo import Graph, Node


class GraphFoundation():
    def __init__(self):
        print("GraphFoundation init...")
        self.summoner_path = '../data/summoner.json'
        self.equipment_path = '../data/item.json'
        self.g = Graph("http://localhost:7474", username="neo4j", password="123456")
        self.summoner_data = {}
        self.equipment_data = {}
        '''summoner_id-big.jpg'''
        self.summoner_img_prefix = "https://game.gtimg.cn/images/yxzj/img201606/summoner/"
        '''item_id.jpg'''
        self.equipment_img_prefix = "https://game.gtimg.cn/images/yxzj/img201606/itemimg/"

    def read_summoner_json(self):
        with open(self.summoner_img_prefix, 'r', encoding='utf-8')as fp:
            self.summoner_data = json.load(fp)

    def read_equipment_json(self):
        with open(self.equipment_path, 'r', encoding='utf-8')as fp:
            self.equipment_data = json.load(fp)

    '''建立召唤师技能节点'''

    def create_summoner_node(self, label, nodes):
        print(f"create_node   label:{label}")
        for item in nodes:
            print(f"正在处理  label:{label}  summoner_name:{item['summoner_name']}")
            node = Node(label, name=item['summoner_name'], summoner_id=item['summoner_id'],
                        summoner_rank=item['summoner_rank'], summoner_description=item['summoner_description'],
                        summoner_img_url=f'{self.summoner_img_prefix}{item["summoner_id"]}-big.jpg')
            self.g.create(node)
        return

    '''建立装备节点'''

    def create_equipment_node(self, label, nodes):
        print(f"create_node   label:{label}")
        for item in nodes:
            print(f"正在处理  label:{label}  equipment_name:{item['item_name']}")
            if (self.isExtend(item, "des2") == True):
                node = Node(label, name=item['item_name'], summoner_id=item['item_id'],
                            item_type=item['item_type'], price=item['price'], total_price=item['total_price'],
                            des1=item['des1'], des2=item['des2'],
                            equipment_img_url=f'{self.equipment_img_prefix}{item["item_id"]}.jpg')
            else:
                node = Node(label, name=item['item_name'], summoner_id=item['item_id'],
                            item_type=item['item_type'], price=item['price'], total_price=item['total_price'],
                            des1=item['des1'],
                            equipment_img_url=f'{self.equipment_img_prefix}{item["item_id"]}.jpg')

            self.g.create(node)
        return

    def start(self):
        # self.read_summoner_json()
        # self.create_summoner_node("summoner", self.summoner_data)
        self.read_equipment_json()
        self.create_equipment_node("equipment", self.equipment_data)

    def isExtend(self, item, param):
        for key in item:
            if (param == key):
                return True
        return False


if __name__ == '__main__':
    g = GraphFoundation()
    g.start()
