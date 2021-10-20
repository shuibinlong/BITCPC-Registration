from django.db import models
from froala_editor.fields import FroalaField


class HomePage(models.Model):
    class Meta:
        verbose_name = '主页设置'
        verbose_name_plural = '主页设置'
    title = models.TextField('主页标题')
    title_top = models.TextField('抬头标题', null=True, blank=True)
    description = models.TextField('简短描述', null=True, blank=True)
    contact_us = FroalaField('联系我们内容', null=True, blank=True)

    def __str__(self):
        return "主页设置"


class HomePageImage(models.Model):
    class Meta:
        verbose_name = '主页滚动图片'
        verbose_name_plural = '主页滚动图片'
    image = models.ImageField('滚动图片', null=True, upload_to='img/')
    homepage = models.ForeignKey(HomePage, on_delete=models.CASCADE)
    title = models.TextField('图片介绍', default='')


class Notice(models.Model):
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
    title = models.TextField('通知标题')
    content = FroalaField()
    pub_date = models.DateTimeField('发布日期')
    author = models.CharField('作者', max_length=40)

    def __str__(self):
        return self.title


class NoticeFile(models.Model):
    class Meta:
        verbose_name = '附件列表'
        verbose_name_plural = '附件列表'
    file = models.FileField('附件', null=True, upload_to='file/')
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)
