import pandas as pd
import pymysql
from sqlalchemy import create_engine

engine = create_engine("mysql://root:root@localhost/spam?charset=utf8")

# df = pd.read_csv('datafile/带标签信息.txt',sep='\t',names=['lable','youjian'])
# df.index.name = 'id'
# df.to_sql('web_dataset',engine,if_exists='append')

df1 = pd.read_csv('D:/桌面/基于机器学习电信诈骗系统/Amachine/SPAM/datafile/stopwords.txt', names=['name'])
df1.index.name = 'id'
df1.to_sql('web_stopword', engine, if_exists='append')

# import joblib
# try:
#     vec_tfidf = joblib.load("datafile/vec_tfidf")
#     modelb = joblib.load('model/SVM_sklearn.pkl')
#     print("文件加载成功")
# except Exception as e:
#     print(f"文件加载失败, 原因: {e}")
