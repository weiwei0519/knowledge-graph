# coding=UTF-8
# 基于wiki百科500多篇关于电影的文本，提取主语和宾语。

'''
@File: KG_wiki_en
@Author: WeiWei
@Time: 2022/11/26
@Email: weiwei_519@outlook.com
@Software: PyCharm
'''

import re
import pandas as pd
import bs4
import requests
import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher
from spacy.tokens import Span

import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm  # 进度条

pd.set_option('display.max_colwidth', 200)

# import wikipedia sentences
candidate_sentences = pd.read_csv("wiki_movie_v2.csv")
print("sentences number is: " + str(candidate_sentences.shape))

candidate_sentences['sentence'].sample(5).info


## 主语和宾语提取
def entity_extract(sent):
    ent1 = ""
    ent2 = ""
    # prv tok dep和prv tok text将分别保留句子中前一个单词和前一个单词本身的依赖标签。前缀和修饰符将保存与主题或对象相关的文本。
    prv_tok_dep = ""  # dependency tag of previous token in the sentence
    prv_tok_text = ""  # previous token in the sentence
    prefix = ""
    modifier = ""

    for tok in nlp(sent):
        # print(tok.text, "...", tok.dep_)
        # 接下来，我们将遍历句子中的记号。我们将首先检查标记是否为标点符号。如果是，那么我们将忽略它并转移到下一个令牌。
        # 如果标记是复合单词的一部分(dependency tag = compound)，我们将把它保存在prefix变量中。
        # 复合词是由多个单词组成一个具有新含义的单词(例如“Football Stadium”, “animal lover”)。
        # 当我们在句子中遇到主语或宾语时，我们会加上这个前缀。我们将对修饰语做同样的事情，例如“nice shirt”, “big house”
        # if token is a punctuation mark then move on to the next token
        if tok.dep_ != "punct":
            # check: token is a compound word or not
            if tok.dep_ == "compound":
                prefix = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " " + tok.text

            # check: token is a modifier or not, mod 是一个修饰词
            if tok.dep_.endswith("mod") == True:
                modifier = tok.text
                # if the previous word was also a 'compound' then add the current word to it
                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " " + tok.text

            ## chunk 3
            # 在这里，如果令牌是主语，那么它将作为ent1变量中的第一个实体被捕获。变量如前缀，修饰符，prv tok dep，和prv tok文本将被重置。
            if tok.dep_.find("subj") == True:  # 包含subj的均为主语，例如：nsubj名词性主语，csubj从句主语
                ent1 = modifier + " " + prefix + " " + tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""

            ## chunk 4
            # 在这里，如果令牌是宾语，那么它将被捕获为ent2变量中的第二个实体。变量，如前缀，修饰符，prv tok dep，和prv tok文本将再次被重置。
            if tok.dep_.find("obj") == True:  # 包含obj的为宾语，例如：dobj为直接宾语，pobj为介词宾语
                ent2 = modifier + " " + prefix + " " + tok.text

            ## chunk 5
            # 一旦我们捕获了句子中的主语和宾语，我们将更新前面的标记和它的依赖标记。
            # update variables
            prv_tok_dep = tok.dep_
            prv_tok_text = tok.text

    return [ent1.strip(), ent2.strip()]


## 关系提取
# 函数中定义的模式试图找到句子中的词根或主要动词。一旦确定了词根，该模式就会检查它后面是介词(prep)还是代理词。如果是，则将其添加到根词中。
def relation_extract(sentence):
    # for tok in nlp(sentence):
    #     print(tok.text, "...", tok.dep_)
    sent = nlp(sentence)
    matcher = Matcher(nlp.vocab)
    # 定义pattern
    pattern = [{'DEP': 'ROOT'},
               {'DEP': 'prep', 'OP': "?"},
               {'DEP': 'agent', 'OP': "?"},
               {'POS': 'ADJ', 'OP': "?"}]
    matcher.add("matching_1", [pattern])
    matches = matcher(sent)
    k = len(matches) - 1
    span = sent[matches[k][1]:matches[k][2]]
    return span.text


# entity extract testing example
# print(entity_extract("japanese developer hideo kojima  is considered to be the first auteur of video games."))
# relation extract tesing example
print(relation_extract("confused and frustrated, connie decides to leave on her own."))

# 提取训练集sentence的：主语——宾语 的pairs
entity_pairs = []

for sent in tqdm(candidate_sentences["sentence"]):
    entity_pairs.append(entity_extract(sent))

# 提取训练集sentence的：谓语
relations = [relation_extract(i) for i in tqdm(candidate_sentences['sentence'])]

# 打印输出
# ds = [[l, i[0], j, i[1]] for l, i, j in zip(range(len(entity_pairs)), entity_pairs, relations)]
# df = pd.DataFrame(ds, columns=['No', 'Subj', 'Root', 'Obj'])
# print(df)

# extract subject
source = [i[0] for i in entity_pairs]
# extract object
target = [i[1] for i in entity_pairs]

kg_df = pd.DataFrame({'source': source, 'target': target, 'edge': relations})
print(kg_df)

# create a directed-graph from a dataframe for all entities
G = nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())

plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G)
nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos=pos)
plt.show()

# create a KG for composed-by entities
G = nx.from_pandas_edgelist(kg_df[kg_df['edge'] == "composed by"], "source", "target", edge_attr=True,
                            create_using=nx.MultiDiGraph())

plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.5)  # k regulates the distance between nodes
nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)
plt.show()

# create a KG for written-by entities
G = nx.from_pandas_edgelist(kg_df[kg_df['edge'] == "written by"], "source", "target", edge_attr=True,
                            create_using=nx.MultiDiGraph())


plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.5)
nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos = pos)
plt.show()
