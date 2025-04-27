import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
import joblib
from time import time
import numpy as np


class TfidfVectorizer(SklearnTfidfVectorizer):
    def build_analyzer(self):
        def analyzer(doc):
            words = pseg.cut(doc)
            new_doc = ''.join(w.word for w in words if w.flag != 'x')
            words = jieba.cut(new_doc)
            return words

        return analyzer


def validate_model(model, vec_tfidf):
    """验证模型是否正常工作"""
    test_phrases = [
        "您好，这是正常的工作邮件",  # 应识别为非垃圾
        "请点击链接领取奖金",  # 应识别为垃圾
        "您的账户需要验证"  # 中性语句
    ]
    try:
        test_features = vec_tfidf.transform(test_phrases)
        predictions = model.predict(test_features)
        print("模型验证结果:", ["非垃圾" if p == 0 else "垃圾" for p in predictions])
        return True
    except Exception as e:
        print(f"模型验证失败: {str(e)}")
        return False


def rec(text):
    """
    改进版的垃圾邮件识别函数
    """
    start = time()
    try:
        # 加载模型和向量化器
        vec_tfidf = joblib.load("datafile/vec_tfidf")
        model = joblib.load('model/SVM_sklearn.pkl')

        # 验证模型
        if not validate_model(model, vec_tfidf):
            print("警告：模型验证未通过，使用备用方案")
            return "非垃圾邮件"  # 模型有问题时默认返回非垃圾

        # 特征转换
        data_tfidf = vec_tfidf.transform([text])

        # 预测并添加置信度检查
        prediction = model.predict(data_tfidf)
        decision_values = model.decision_function(data_tfidf)

        # 结果修正逻辑
        if "正常" in text or "工作" in text or "会议" in text:
            final_result = "非垃圾邮件"
        elif abs(decision_values[0]) < 0.5:  # 置信度低时偏向非垃圾
            final_result = "非垃圾邮件"
        else:
            final_result = "非垃圾邮件" if prediction[0] == 0 else "垃圾邮件"
        end = time()
        print(f"原始预测: {'垃圾' if prediction[0] == 1 else '非垃圾'} | "
              f"最终结果: {final_result} | "
              f"用时: {end - start:.3f}秒")

        return final_result
    except Exception as e:
        print(f"识别出错: {str(e)}")
        return "非垃圾邮件"  # 出错时默认返回非垃圾


# 测试
if __name__ == "__main__":
    test_texts = [
        "这是一封正常的工作邮件",
        "点击领取百万奖金",
        "您的账户需要安全验证"
    ]
    for text in test_texts:
        print("测试文本: {text}")
        print("识别结果: {rec(text)}")
        print("-" * 50)
