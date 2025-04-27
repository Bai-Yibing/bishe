# -*- coding: utf-8 -*-

import codecs

from collections import Counter
import jieba
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud


def not_tag_data():
    with codecs.open('datafile/带标签信息.txt', 'r', 'utf-8') as f:
        data = [line.strip() for line in f.read().split('\n')]
        if data[-1] == '':
            data.pop()
        i = 0
        testdata = []
        for item in data:
            if str(item).split('\t')[0] == '0':
                testdata.append(str(item).split('\t')[1])
                i += 1
                if i > 8000:
                    break
        print()
        print(testdata)
    return testdata


def f(x):
    return Counter(jieba.cut(x))


def bWordCloud(dataList):
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    stopwords = set()
    content = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords.update(content)
    finaldata = ""
    for dataitem in dataList:
        finaldata += dataitem
    img = Image.open('test.jpg')
    img_array = np.array(img)
    finaldata = " ".join(jieba.cut(finaldata))
    wordCloud = WordCloud(
        font_path="C:\\Windows\\Fonts\\simfang.ttf",
        background_color="white",
        stopwords=stopwords,
        mask=img_array,
        scale=18
    ).generate(finaldata)
    plt.imshow(wordCloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig('Cloud.jpg')
    plt.show()


def tjieba(dataList):
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
    stopwords = set()
    content = [line.strip() for line in open('stopwords.txt', 'r', encoding='utf-8').readlines()]
    stopwords.update(content)
    finaldata = ""
    for dataitem in dataList:
        finaldata += dataitem
    finaldata = " ".join(jieba.cut(finaldata))
    print('原始数据:')
    print(dataList)
    # print('分词结果:')
    # print(finaldata)
    sw = []
    for i in jieba.cut(finaldata):
        if i != ' ' and i not in stopwords:
            sw.append(i)
    print('去停用词结果:')
    print(sw)


if __name__ == "__main__":
    # data = not_tag_data()
    # bWordCloud(data)
    tjieba(['亲，金汕教育春季班从x月x号起陆续开班啦！报名热线xxxxxxxx，或者直接回复需要补习的年级科目，我们会尽快跟您联系的。', '凌晨快清晨了还在医院里我真的不想病倒'])
