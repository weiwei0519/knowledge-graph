# coding=UTF-8
# spacy util function

'''
@File: spacy_util
@Author: WeiWei
@Time: 2022/11/26
@Email: weiwei_519@outlook.com
@Software: PyCharm
'''

# pip install -U spacy
import spacy

## pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.4.1/en_core_web_sm-3.4.1.tar.gz
## pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.4.1/en_core_web_md-3.4.1.tar.gz
## pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.4.1/en_core_web_lg-3.4.1.tar.gz
## pip install https://github.com/explosion/spacy-models/releases/download/zh_core_web_trf-3.4.0/zh_core_web_trf-3.4.0.tar.gz
## pip install https://github.com/explosion/spacy-models/releases/download/zh_core_web_sm-3.4.0/zh_core_web_sm-3.4.0.tar.gz
## pip install F:\Software\Python\spaCy\models\zh_core_web_sm-3.4.0.tar.gz
# sm=small  md=middle   lg=large  trf=largest and slow
nlp = spacy.load('en_core_web_sm')
sentence = "The 22-year-old recently won ATP Challenger tournament."
print("Sentence: " + sentence)
sent = nlp(sentence)
for word in sent:
  print(word.text, "...", word.dep_)

sentence = "Nagal won the first set."
print("\n" + "Sentence: " + sentence)
sent = nlp(sentence)
for word in sent:
  print(word.text, "...", word.dep_)