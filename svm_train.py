import os
import jieba
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score
from scipy.stats import uniform


class EmailToWordFeatures:
    '''
    功能:将邮件转换为特征词矩阵
    整个过程包括：
    - 对邮件内容进行分词处理
    - 去除所有非中文字符，如标点符号、英文字符、数字、网站链接等特殊字符
    - 过滤停用词
    - 创建特征矩阵
    '''

    def __init__(self, stop_word_file=None, features_vocabulary=None):

        self.features_vocabulary = features_vocabulary

        self.stop_vocab_dict = {}  # 初始化停用词
        if stop_word_file is not None:
            self.stop_vocab_dict = self._get_stop_words(stop_word_file)

    def text_to_feature_matrix(self, words, vocabulary=None, threshold=10):
        cv = CountVectorizer()
        if vocabulary is None:
            cv.fit(words)
        else:
            cv.fit(vocabulary)
        words_to_vect = cv.transform(words)
        words_to_matrix = pd.DataFrame(words_to_vect.toarray())  # 转换成索引矩阵
        print(words_to_matrix.shape)

        # 进行训练特征词选择，给定一个阈值，当单个词在所有邮件中出现的次数的在阈值范围内时及选为训练特征词、
        selected_features = []
        selected_features_index = []
        for key, value in cv.vocabulary_.items():
            if words_to_matrix[value].sum() >= threshold:  # 词在每封邮件中出现的次数与阈值进行比较
                selected_features.append(key)
                selected_features_index.append(value)
        words_to_matrix.rename(columns=dict(zip(selected_features_index, selected_features)), inplace=True)
        return words_to_matrix[selected_features]

    def get_email_words(self, email_path, max_email=600):
        '''
        由于机器配置问题，作为测试给定阈值600，及正负样本数各位600
        '''
        self.emails = email_path
        if os.path.isdir(self.emails):
            emails = os.listdir(self.emails)
            is_dir = True
        else:
            emails = [self.emails, ]
            is_dir = False

        count = 0
        all_email_words = []
        for email in emails:
            if count >= max_email:  # 给定读取email数量的阈值
                break
            if is_dir:
                email_path = os.path.join(self.emails, email)
            email_words = self._email_to_words(email_path)
            all_email_words.append(' '.join(email_words))
            count += 1
        return all_email_words

    def _email_to_words(self, email):
        '''
        将邮件进行分词处理，去除所有非中文和停用词
        retrun:words_list
        '''
        email_words = []
        with open(email, 'rb') as pf:
            for line in pf.readlines():
                line = line.strip().decode('gbk', 'ignore')
                if not self._check_contain_chinese(line):  # 判断是否是中文
                    continue
                word_list = jieba.cut(line, cut_all=False)  # 进行分词处理
                for word in word_list:
                    if word in self.stop_vocab_dict or not self._check_contain_chinese(word):
                        continue  # 判断是否为停用词
                    email_words.append(word)
            return email_words

    def _get_stop_words(self, file):
        '''
        获取停用词
        '''
        stop_vocab_dict = {}
        with open(file, 'rb') as pf:
            for line in pf.readlines():
                line = line.decode('utf-8', 'ignore').strip()
                stop_vocab_dict[line] = 1
        return stop_vocab_dict

    def _check_contain_chinese(self, check_str):
        '''
        判断邮件中的字符是否有中文
        '''
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False


index_file = '.\\datasets\\trec06c\\full\\index'
stop_word_file = '.\\datasets\\trec06c\\chinese_stop_vocab.txt'
ham_file = '.\\datasets\\trec06c\\ham_data'
spam_file = '.\\datasets\\trec06c\\spam_data'

email_to_features = EmailToWordFeatures(stop_word_file=stop_word_file)
ham_words = email_to_features.get_email_words(ham_file)
spam_words = email_to_features.get_email_words(spam_file)
print('ham email numbers:', len(ham_words))
print('spam email numbers:', len(spam_words))

all_email = []
all_email.extend(ham_words)
all_email.extend(spam_words)
print('all test email numbers:', len(all_email))
words_to_matrix = email_to_features.text_to_feature_matrix(all_email)
print(words_to_matrix)

label_matrix = np.zeros((len(all_email), 1))
label_matrix[0:len(ham_words), :] = 1

# 拆分数据集
x_train, x_test, y_train, y_test = train_test_split(words_to_matrix, label_matrix, test_size=0.2, random_state=42)

# 使用LinearSVC模型进行训练
svc = LinearSVC(loss='hinge', dual=True)
param_distributions = {'C': uniform(0, 10)}
rscv_clf = RandomizedSearchCV(estimator=svc, param_distributions=param_distributions, cv=3, n_iter=200, verbose=2)
rscv_clf.fit(x_train, y_train)
print('best_params:', rscv_clf.best_params_)

# 使用测试数据集进行测试
y_prab = rscv_clf.predict(x_test)
print('accuracy:', accuracy_score(y_prab, y_test))
