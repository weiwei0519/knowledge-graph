# coding=UTF-8
# 构建红楼梦的人物关系知识图谱

'''
@File: KG_HLM_zh.py
@Author: WeiWei
@Time: 2022/11/27
@Email: weiwei_519@outlook.com
@Software: PyCharm
'''

import csv
import py2neo
from py2neo import Graph, Node, Relationship, NodeMatcher, Subgraph
import logging
import sys
from neo4j_util import Neo4j

# 账号密码改为自己的即可
g = Graph('http://localhost:7474', user='neo4j', password='neo4j123')
with open('HLM_relation.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for item in reader:
        if reader.line_num == 1:
            continue
        tx = g.begin()
        print("当前行数：", reader.line_num, "当前内容：", item)
        start_node = Node("Person", name=item[0])
        end_node = Node("Person", name=item[1])
        relation = Relationship(start_node, item[3], end_node)
        tx.merge(start_node, "Person", "name")
        tx.merge(end_node, "Person", "name")
        tx.merge(relation, "Person", "name")
        tx.commit()


def batch_create(graph, nodes_list, relations_list):
    """
        批量创建节点/关系,nodes_list和relations_list不同时为空即可
        特别的：当利用关系创建节点时，可使得nodes_list=[]
    :param graph: Graph()
    :param nodes_list: Node()集合
    :param relations_list: Relationship集合
    :return:
    """

    subgraph = Subgraph(nodes_list, relations_list)
    tx_ = graph.begin()
    tx_.create(subgraph)
    graph.commit(tx_)


# if __name__ == '__main__':
#     # 连接neo4j
#     neo4j_bolt_url = "bolt://localhost:7687"
#     user = "neo4j"
#     password = "neo4j123"
#     Neo4j.enable_log(logging.INFO, sys.stdout)
#     kg_db = Neo4j(neo4j_bolt_url, user, password)
#
#     with open('HLM_relation.csv', 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         for item in reader:
#             if reader.line_num == 1:
#                 continue
#             print("当前行数：", reader.line_num, "当前内容：", item)
#             start_node = Node("Person", name=item[0])
#             end_node = Node("Person", name=item[1])
#             relation = Relationship(start_node, item[3], end_node)
#             g.merge(start_node, "Person", "name")
#             g.merge(end_node, "Person", "name")
#             g.merge(relation, "Person", "name")
