#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:Liu Fuxiang time:2019-06-20
#正则表达式对原始语料库进行预处理
import codecs
import re
def Init():
    fin=codecs.open("train2.txt","r","utf-8")
    strl=fin.read()
    strl = re.sub("\[","",strl)
    strl = re.sub("]nt","",strl)
    strl = re.sub("]ns","",strl)
    strl = re.sub("]nz","",strl)
    strl = re.sub("]l","",strl)
    strl = re.sub("]i","",strl)
    strl = re.sub("\n", "@", strl)
    strl = re.sub("\s+"," ", strl)
    strl = re.sub("@","\n",strl)
    strl = re.sub(" \n","\n",strl)
    strl = re.sub(" ","@",strl)
    strl = re.sub("\s+","\n",strl)
    strl = re.sub("@"," ",strl)
    #s=strl.encode("utf-8")
    fout=open("afterTrain2.txt","w")
    fout.write(strl)
    fout.close()
    fin.close()


