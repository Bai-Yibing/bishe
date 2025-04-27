from django.contrib import admin
from .models import *


class UnderwriterDataset(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'youjian', 'lable',)


class UnderwriterStopword(admin.ModelAdmin):
    # 需要显示的字段信息
    list_display = ('id', 'name')


admin.site.site_title = "基于SVM的垃圾邮件过滤系统"
admin.site.site_header = "基于SVM的垃圾邮件过滤系统"
admin.site.register(Dataset, UnderwriterDataset)
admin.site.register(Stopword, UnderwriterStopword)
