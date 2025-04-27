from numpy import *
import json
import numpy as np
import jieba
import jieba.posseg as pseg
import sklearn.feature_extraction.text
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA
from scipy import sparse, io
from time import time
import sys
import joblib


# log

class TfidfVectorizer(sklearn.feature_extraction.text.TfidfVectorizer):
    def build_analyzer(self):
        def analyzer(doc):
            words = pseg.cut(doc)
            new_doc = ''.join(w.word for w in words if w.flag != 'x')
            words = jieba.cut(new_doc)
            return words

        return analyzer


class Logger(object):
    def __init__(self, fileN="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


sys.stdout = Logger("mylog.txt")


def dimensionality_reduction(x, type='pca'):
    if type == 'pca':
        n_components = 500
        t0 = time()
        pca = PCA(n_components=n_components)
        pca.fit(x)
        x_transform = sparse.csr_matrix(pca.transform(x))
        print("PCA reduction done in %0.3fs" % (time() - t0))
        return x_transform
    if type == 'nmf':
        n_components = 500
        t1 = time()
        nmf = NMF(n_components=n_components)
        nmf.fit(x)
        x_transform = sparse.csr_matrix(nmf.transform(x))
        print("NMF reduction done in %0.3fs" % (time() - t1))
        return x_transform


if '__main__' == __name__:
    t0 = time()
    data_lines = 50000  # data lines, can be modified
    data_type = "raw"  # proccessed data type {raw, pca, nmf, pca&nmf}
    x = []
    y = []
    lines = []

    with open('datafile/带标签信息.txt', encoding='utf-8') as fr:  # same as try ... finally，but more simpler
        for i in range(data_lines):
            line = fr.readline()
            message = line.split('\t')
            y.append(message[0])
            x.append(message[1])

    with open('datafile/result.json', 'w') as f:
        json.dump(y, f)
    print("save y successfully!")

    vec_tfidf = TfidfVectorizer()
    data_tfidf = vec_tfidf.fit_transform(x)

    joblib.dump(vec_tfidf, "datafile/vec_tfidf")
    print("save vec_tfidf successfully!")

    if data_type == 'raw':
        io.mmwrite('datafile/X.mtx', data_tfidf)
        print("save X successfully!")

    name_tfidf_feature = vec_tfidf.get_feature_names()
    with open('datafile/feature.json', 'w') as f:
        json.dump(name_tfidf_feature, f)
    print("save feature successfully!")

    if data_type == 'nmf' or data_type == 'pca&nmf':
        nmf = dimensionality_reduction(data_tfidf.todense(), type='nmf')
        io.mmwrite('datafile/X.mtx', nmf)
        print("save nmf successfully!")

    if data_type == 'pca' or data_type == 'pca&nmf':
        pca = dimensionality_reduction(data_tfidf.todense(), type='pca')
        io.mmwrite('datafile/X.mtx', pca)
        print("save pca successfully!")

    print("******* %s lines data preprocessing done in %0.3fs *******\n\n" % (data_lines, (time() - t0)))
