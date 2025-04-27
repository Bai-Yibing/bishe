# coding=utf-8
import jieba.posseg as pseg
import joblib
import sys
from time import time

start = time()
model = joblib.load("./model/dtree_py2_final.m")

X1 = []
X2 = []

gpus = sys.argv[1]
X1.append(gpus)

for i in range(len(X1)):
    words = pseg.cut(X1[i])
    str1 = ""
    for key in words:
        str1 += key.word
        str1 += ' '
    X2.append(str1)  # 短信内容

vectorizer = joblib.load("datafile/tfidf_py2_final.m")  # 实例化
x_demand_prediction = vectorizer.transform(X2)

y_predict = model.predict(x_demand_prediction)
end = time()

for i in range(len(X1)):
    if int(y_predict[i]) == 0:
        print("yes")
    else:
        print("no")
