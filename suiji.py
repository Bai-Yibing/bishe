from scipy import io
import json
import pandas as pd
import numpy as np
from train import select_data

'''
随机森林预测
'''

takeup = 0.1
x = io.mmread('datafile/X.mtx')
with open('datafile/result.json', 'r') as f:
    y = json.load(f)
# 将数据分解为训练集和测试集
train_features, test_features, train_labels, test_labels = select_data(x, y, takeup)

print('Training Features Shape:', train_features.shape)
print('Testing Features Shape:', test_features.shape)

# 初始模型
from sklearn.tree import export_graphviz
from sklearn.ensemble import RandomForestRegressor
import pydot  # pip install pydot

# 限制树的深度为2级
af_small = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
af_small.fit(train_features, train_labels)
# 提取小树
tree1 = af_small.estimators_[5]
# 将树保存为png图像
export_graphviz(tree1, out_file='tree1.dot', rounded=True, precision=1)
(graph,) = pydot.graph_from_dot_file('tree1.dot')  # Graphviz
graph.write_png('tree1.png')
# 精确度检查
# 对试验数据采用森林预测法
predictions = af_small.predict(test_features)
# 算绝对误差
predictions = predictions.tolist()
mape = 0
for i in range(len(test_labels)):
    if int(test_labels[i]) == int(predictions[i]):
        mape += 1

print('Accuracy:', 100 * round(mape / len(test_labels), 2), '%.')
