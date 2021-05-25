# -*- coding: utf-8 -*-
# @Time : 2021/5/25 15:17
# @Author : raptor
# @File : QuerySth.py
import os
import json
from py2neo import Graph, Node


class QuerySth():
    def __init__(self):
        self.g = Graph("http://localhost:7474", username="neo4j", password="123456")

    def query(self):
        query = 'match(p:hero) where p.name="吕布" return p'
        cursor = self.g.run(query).data()
        for record in cursor:
            print(record)


if __name__ == '__main__':
    sth = QuerySth()
    sth.query()
