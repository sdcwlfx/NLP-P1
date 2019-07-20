#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:Liu Fuxiang time:2019-06-17
#https://blog.csdn.net/weixin_42398658/article/details/85048917

import preInit
import HMM
import jieba
import time

#读入字典dic.txt
class WordSegmentation:
    def __init__(self):
        # 初始化字典用来存储字典词
        self.dictionary = {}
        # 正向匹配分词结果
        self.forwardResult = ""
        # 逆向匹配分词结果
        self.backwardResult = ""


        # 记录前向总词数
        self.forwardNum = 0
        # 记录逆向总词数
        self.backwardNum = 0

        # 记录前向匹配中非字典的词数
        self.forwardNotNum = 0
        # 记录逆向匹配中非字典的词数
        self.backwardNotNum = 0

        #单字词数,越少越好
        self.forwardSingleWordNum=0
        self.backwardSingleWordNum=0

        #计算频率乘积
        self.forwardFrq=1
        self.backwardFrq=1

    # 读取字典数据
    def readDic(self, path):
        # 只读打开文件
        f = open(path, 'r')
        for line in f.readlines():
            line = line.strip('\n')
            # self.dictionary.append(line)
            if (line not in self.dictionary):
                self.dictionary[line] = 1
            else:
                self.dictionary[line] += 1

    #从人民日报语料库中读取字典信息并统计词频
    def readPeopleDayDic(self,pathDay):
        f=open(pathDay,'r')
        while (True):
            text = f.readline().strip("\n")#除去最后的换行符'\n'
            if (text == ""):
                break
            tmp = text.split(" ")
            n = len(tmp)
            for i in range(n):
                word = tmp[i].split('/')
                if(word[0] not in self.dictionary):
                    self.dictionary[word[0]]=1
                else:
                    self.dictionary[word[0]]+=1

    #设置字典
    def setDictionary(self,dic):
        self.dictionary=dic

    #打印字典数据
    def showDic(self):
        print(str(self.dictionary))

    #正向匹配
    def forwardSegmentation(self,textC,maxLen):
        if(maxLen>len(textC)):
            length=len(textC)
        else:
            length=maxLen
        start=0
        while(start<=len(textC)-1):
            if(start+length>len(textC)):
                temp=textC[start:]
            else:
                temp=textC[start:start+length]
            while(len(temp)>1):
                #判断是否在字典中
                if(temp in self.dictionary):
                    self.forwardResult+=temp+"/"
                    start+=len(temp)
                    self.forwardNum+=1
                    self.forwardFrq*=self.dictionary[temp]
                    break
                else:
                    temp=temp[:len(temp)-1]
            #单个词则直接分词
            if(len(temp)==1):
                self.forwardResult+=temp+"/"
                start+=1
                self.forwardNum+=1
                self.forwardSingleWordNum+=1
                #不在字典中,更新非字典词计数
                if(temp not in self.dictionary):
                    self.forwardNotNum+=1
                else:
                    self.forwardFrq*=self.dictionary[temp]


        #去掉最后的"/'
        self.forwardResult=self.forwardResult[:-1]
        print("MM分词结果："+self.forwardResult)

    #逆向匹配
    def backwardSegmentation(self,textC,maxLen):
        if (maxLen > len(textC)):
            length = len(textC)
        else:
            length = maxLen
        start = 0
        end=0
        while(len(textC)+end>0):
            if(end==0):
                start=-length
                temp=textC[start:]
            else:
                if(len(textC)+(end-length)>=0):
                    start=end-length
                    temp=textC[start:end]
                else:
                    start=-len(textC)
                    temp=textC[start:end]
            while (len(temp) > 1):
                # 判断是否在字典中
                if (temp in self.dictionary):
                    self.backwardResult =temp+"/"+self.backwardResult
                    end -= len(temp)
                    self.backwardNum+=1
                    self.backwardFrq*=self.dictionary[temp]
                    break
                else:
                    temp = temp[1-len(temp):]
            # 单个词则直接分词
            if (len(temp) == 1):
                self.backwardResult = temp + "/"+self.backwardResult
                end-=1
                self.backwardNum+=1
                self.backwardSingleWordNum+=1
                if(temp not in self.dictionary):
                    self.backwardNotNum+=1
                else:
                    self.backwardFrq*=self.dictionary[temp]
        # 去掉最后的"/'
        self.backwardResult = self.backwardResult[:-1]
        print("RMM分词结果：" + self.backwardResult)

#jieba分词作为标准结果
def jiebaResult(string):
    seg_list=list(jieba.cut(string))
    return seg_list


#计算分词正确率、分词召回率
def segCorrectnessRateAndRecallRate(finalResult,jiebaList):
    finalResult=finalResult.split('/')
    #计数切分出的词语出现在标准结果中的词语数
    count=0
    #切分出的词语总数
    segWordsNum=len(finalResult)
    #标准结果中的词语总数
    jiebaWordsNum=len(jiebaList)
    for word in finalResult:
        if(word in jiebaList):
            count+=1
    correctnessRate=count/segWordsNum
    recallRate=count/jiebaWordsNum
    return correctnessRate,recallRate

def main():
    ws=WordSegmentation()

    #预处理语料库数据
    # preInit.Init()
    hmm = HMM.HMM()

    #ws.readPeopleDayDic('afterTrain2.txt')
    finalResult=""
    #字典路径
    # path='dic.txt'
    # ws.readDic(path)
    #ws.showDic()
    textC=input("请输入一段文本:\n").strip("\n")

    maxLen=int(input("词最大长度:\n"))

    # 分词开始时间戳
    startTicks = time.time()
    # 读取语料库中所有词及词性
    hmm.readAllWordAndPOS()
    ws.setDictionary(hmm.getDic())

    print("开始时间戳",startTicks)
    #正向匹配
    ws.forwardSegmentation(textC,maxLen)
    #逆向匹配
    ws.backwardSegmentation(textC,maxLen)
    #分词数越少越好
    if(ws.backwardNum<ws.forwardNotNum):
        print("最终分词结果："+ws.backwardResult)
        finalResult=ws.backwardResult
    elif(ws.backwardNum>ws.forwardNum):
        print("最终分词结果："+ws.forwardResult)
        finalResult=ws.forwardResult
    else:
        #非字典词越少越好
        if(ws.backwardNotNum<ws.forwardNotNum):
            print("最终分词结果："+ws.backwardResult)
            finalResult=ws.backwardResult
        elif(ws.backwardNotNum>ws.forwardNotNum):
            print("最终分词结果："+ws.forwardResult)
            finalResult=ws.forwardResult
        else:
            #单词数越少越好
            if(ws.backwardSingleWordNum<ws.forwardSingleWordNum):
                print("最终分词结果："+ws.backwardResult)
                finalResult=ws.backwardResult
            elif(ws.backwardSingleWordNum>ws.forwardSingleWordNum):
                print("最终分词结果："+ws.forwardResult)
                finalResult=ws.forwardResult
            else:
                #消除歧义,频率乘积越大越好
                if(ws.backwardFrq>ws.forwardFrq):
                    print("最终分词结果："+ws.backwardResult)
                    finalResult=ws.backwardResult
                else:
                    print("最终分词结果："+ws.forwardResult)
                    finalResult=ws.forwardResult
    #分词结束时间戳
    endTicks=time.time()
    print(endTicks-startTicks)

    segTime = len(finalResult.split("/")) / (endTicks - startTicks)

    #jieba分词作为标准结果
    jieba_list=jiebaResult(textC)
    correctnessRate,recallRate=segCorrectnessRateAndRecallRate(finalResult,jieba_list)
    print("分词正确率："+str(correctnessRate))
    print("分词召回率："+str(recallRate))
    print("分词速度： "+str(segTime))


    #词性标注
    hmm.showAllWordAndPOS()
    hmm.HMMModel(finalResult)




if __name__ == '__main__':
    main()