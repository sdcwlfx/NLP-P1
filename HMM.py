#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:Liu Fuxiang time:2019-06-20
#维特比讲解https://blog.csdn.net/qq_37667364/article/details/81071190
#https://blog.csdn.net/say_c_box/article/details/78550659

import sys
import re
import math
from operator import itemgetter, attrgetter
import ChineseWordSegmentation

class HMM:
    def __init__(self):
        self.dic={}
        # 所有词语
        self.ww = []
        # 所有的词性
        self.pos = []
        # 每个词性出现的频率
        self.fre = {}
        # 初始状态(词性)概率分布
        self.pi = {}
        # 状态转移概率矩阵(状态->下一状态)
        self.A = {}
        # 观测概率矩阵(发射概率矩阵，从状态->输出)
        self.B = {}
        # dp概率(dpij表示处理到第i个单词，该单词词性为j的序列出现的概率)
        self.dp = []
        # 路径记录(保存所有状态的最大值是由哪一个状态产生的也就是计算δ[t](i)时，是由哪一个δ[t-1](q)产生的，q就是哪个状态)
        self.pre = []
        self.zz = {}

    #从语料库中读取所有词性及词语
    def readAllWordAndPOS(self):
        fin = open("afterTrain2.txt", "r")
        while (True):
            text = fin.readline().strip("\n")
            if (text == ""):
                break
            tmp = text.split(" ")
            n = len(tmp)
            for i in range(0, n):
                word = tmp[i].split('/')
                if (word[1] not in self.pos):
                    self.pos.append(word[1])
                if(word[0] not in self.ww):
                    self.ww.append(word[0])
                if(word[0] not in self.dic):
                    self.dic[word[0]]=1
                else:
                    self.dic[word[0]]+=1

    def getDic(self):
        return self.dic

    def showAllWordAndPOS(self):
        for a in self.pos:
            print(a,end=" ")

    #finalSegWords为分词后的句子
    def HMMModel(self,finalSegWords):
        n = len(self.pos)

        # 初始化概率矩阵
        for i in self.pos:
            self.pi[i] = 0
            self.fre[i] = 0
            self.A[i] = {}
            self.B[i] = {}
            for j in self.pos:
                #状态转移矩阵初始化(n*n,n为状态数)
                self.A[i][j] = 0
            for j in self.ww:
                #观测概率矩阵初始化(状态数*词数)
                self.B[i][j] = 0

        # 计算概率矩阵
        line = 0  # 总行数
        fin = open("afterTrain2.txt", "r")
        while (True):
            text = fin.readline()
            if (text == "\n"):
                continue
            if (text == ""):
                break
            tmp = text.split(" ")
            n = len(tmp)
            line += 1

            for i in range(0, n - 1):
                word = tmp[i].split('/')
                pre = tmp[i - 1].split('/')
                self.fre[word[1]] += 1
                if (i == 1):
                    #记住每行第一个分词词性(因为第0个分词都是日期)
                    self.pi[word[1]] += 1
                elif (i > 0):
                    #状态转移矩阵(状态->状态)
                    self.A[pre[1]][word[1]] += 1
                    #发射概率矩阵(状态->输出)
                    self.B[word[1]][word[0]] += 1

        cx = {}
        cy = {}
        for i in self.pos:
            cx[i] = 0
            cy[i] = 0
            #计算初始概率向量(每个词性的初始概率如P(s1)、P(s2)..)
            self.pi[i] = self.pi[i] * 1.0 / line
            #Add-delta平滑防止0概率事件(状态转移矩阵和发射矩阵的平滑处理)
            for j in self.pos:
                if (self.A[i][j] == 0):
                    cx[i] += 1
                    self.A[i][j] = 0.5
            for j in self.ww:
                if (self.B[i][j] == 0):
                    cy[i] += 1
                    self.B[i][j] = 0.5

        for i in self.pos:
            self.pi[i] = self.pi[i] * 1.0 / line
            for j in self.pos:
                #最终的状态转移概率矩阵(P(i,j)/P(i))
                self.A[i][j] = self.A[i][j] * 1.0 / (self.fre[i] + cx[i])
            for j in self.ww:
                self.B[i][j] = self.B[i][j] * 1.0 / (self.fre[i] + cy[i])

        print("\n训练结束\n")

        while (True):
            #tmp = input("请输入需要词性标注的句子，以" / "分割: ")

            if (finalSegWords == "-1"):
                break
            text = finalSegWords.split("/")
            num = len(text)
            # for i in range(0,num):
            # text[i]=unicode(text[i])
            #dpij表示处理到第i个单词，该单词词性为j的序列出现的概率
            self.dp = [{} for i in range(0, num)]
            self.pre = [{} for i in range(0, num)]
            # 初始化概率
            for k in self.pos:
                for j in range(0, num):
                    self.dp[j][k] = 0
                    self.pre[j][k] = ""
            n = len(self.pos)
            for c in self.pos:
                #if (self.B[c].has_key(text[0])):
                if(text[0] in self.B[c]):
                    #P(0,c)=P(c)*P(0|c)
                    self.dp[0][c] = self.pi[c] * self.B[c][text[0]] * 1000
                else:
                    #第一个分词没有c词性时，平滑处理(防止0概率)
                    self.dp[0][c] = self.pi[c] * 0.5 * 1000 / (cy[c] + self.fre[c])
            #时间复杂度（N*N*num，N为状态数，num为分词数）
            for i in range(1, num):
                for j in self.pos:
                    for k in self.pos:
                        tt = 0
                        #if (self.B[j].has_key(text[i])):
                        if(text[i] in self.B[j]):
                            tt = self.B[j][text[i]] * 1000
                        else:
                            tt = 0.5 * 1000 / (cy[j] + self.fre[j])
                        #记录最大概率  max(第i-1个分词词性为k的概率*状态(词性)转移概率*发射概率)
                        if (self.dp[i][j] < self.dp[i - 1][k] * self.A[k][j] * tt):
                            self.dp[i][j] = self.dp[i - 1][k] * self.A[k][j] * tt
                            #记录使得d[i][j]概率最大的第i-1个分词的词性
                            self.pre[i][j] = k
            res = {}
            MAX = ""
            # 先找出最后一个观测的最可能状态(词性)
            for j in self.pos:
                if (MAX == "" or self.dp[num - 1][j] > self.dp[num - 1][MAX]):
                    MAX = j
            if (self.dp[num - 1][MAX] == 0):
                print("您的句子超出我们的能力范围了")
                continue
            i = num - 1
            #回溯路径记录（由最后一个观测得到的最好状态往前回溯找出状态序列）
            while (i >= 0):
                res[i] = MAX
                MAX = self.pre[i][MAX]
                i -= 1
            for i in range(num):
                # print(text[i].decode('utf-8')+"\\"+res[i].decode('utf-8')+",")
                print(text[i] + "/" + res[i],end=" ")
            break


def main():
    pass

if __name__ == '__main__':
    main()





