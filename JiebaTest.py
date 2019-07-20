#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:Liu Fuxiang time:2019-06-20
import jieba
import jieba.posseg

string='他说的确实在理'
#seg=jieba.posseg.cut(string)
seg=list(jieba.cut(string))

# l=[]
# for i in seg:
#     l.append((i.word,i.flag))
print(str(seg))