from django.db import models


# Create your models here.

class Dataset(models.Model):
    id = models.IntegerField(verbose_name='主键', primary_key=True)
    youjian = models.TextField(verbose_name='邮件内容', default='')
    lable = models.IntegerField(verbose_name='分类标签', default=0)

    def __str__(self):
        return self.youjian

    class Meta:
        verbose_name = u"数据集"
        verbose_name_plural = verbose_name


class Stopword(models.Model):
    name = models.CharField(verbose_name='停用词', default='', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"停用词表"
        verbose_name_plural = verbose_name
