import joblib
import numpy as np
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from matplotlib import pyplot as plt
from recognition import rec
from . import models
import pandas as pd
import datetime


@login_required
def index(request):
    if request.method == 'GET':
        # 获取数据集中的前1000条记录
        results = models.Dataset.objects.all()[:1000]
        Search = request.GET.get('Search', '')
        if Search:
            # 如果有搜索条件，使用模糊查询
            results = models.Dataset.objects.filter(youjian__icontains=Search)
        return render(request, 'SPAM/table.html', {'results': results, 'Search': Search})


@login_required
def huizong(request):
    result = None  # 初始化结果变量
    if request.method == 'GET':
        return render(request, 'SPAM/huizong.html', locals())
    elif request.method == 'POST':
        Search = request.POST.get('Search', '')  # 获取前端输入的短信内容
        if Search:
            result = rec(Search)  # 调用 rec() 函数进行短信识别
        return render(request, 'SPAM/huizong.html', {'Search': Search, 'result': result})


@login_required
def fenxi(request):
    if request.method == 'GET':
        # 获取 Count 模型的数据
        datas1 = models.Count.objects.all()
        count_piaofang = []
        count_name = []
        for resu in datas1:
            count_name.append(resu.datetiems)
            count_piaofang.append(resu.piaofang)

        # 获取 bangdan 模型的数据
        datas2 = models.bangdan.objects.all()
        names = list(set([i.name for i in datas2]))
        li1 = []
        for name in names:
            value = models.bangdan.objects.filter(name=name).first().piaofang
            value = int(value) * 10000  # 转换为整数并乘以10000
            li1.append((name, value))
        li1.sort(key=lambda xx: xx[1], reverse=True)  # 按值降序排列

        zuijia_name = []
        zuijia_piaofang = []
        for resu in li1[:10]:
            zuijia_name.append(resu[0])
            zuijia_piaofang.append(resu[1])

        # 统计不同区间的数量
        a1 = len([i for i in li1 if 0 < i[1] < 300000000])
        a2 = len([i for i in li1 if 300000000 < i[1] < 600000000])
        a3 = len([i for i in li1 if 600000000 < i[1] < 1000000000])
        a4 = len([i for i in li1 if 1000000000 < i[1] < 1500000000])
        a5 = len([i for i in li1 if i[1] > 1500000000])
        li11 = [a1, a2, a3, a4, a5]
        pie_names = ['0-3亿', '3-6亿', '6-10亿', '10-15亿', '大于15亿']
        dict_value = []
        for i, name in enumerate(pie_names):
            dict_value.append({"name": name, "value": li11[i]})

        return render(request, 'SPAM/fenxi.html',
                      {'dict_value': dict_value, 'zuijia_name': zuijia_name, 'zuijia_piaofang': zuijia_piaofang})


@login_required
def yuce(request):
    # 获取垃圾短信与非垃圾短信的数量
    datas1 = models.Dataset.objects.filter(lable=0).count()
    datas2 = models.Dataset.objects.filter(lable=1).count()
    dict_value = [{"name": '垃圾邮件', "value": datas1}, {"name": '非垃圾邮件', "value": datas2}]
    return render(request, 'SPAM/yuce.html', {'dict_value': dict_value})
