from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver
from django.core.exceptions import ObjectDoesNotExist

class Person(models.Model):
    class Meta(object):
        verbose_name = '队员'
        verbose_name_plural = '队员'
    name = models.CharField('姓名', max_length=6, null=False)
    student_id = models.CharField('学号', max_length=12, null=False, unique=True)

    CLOTHING_SIZE = (
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
    )
    clothing_size = models.CharField('衣服尺码', max_length=4, choices=CLOTHING_SIZE)
    is_male = models.BooleanField('性别')
    grade = models.CharField('年级，1-4分别表示大一至大四，5为研一，6为博一', max_length=5)
    institute = models.CharField('学院', max_length=10)
    team_belongto = models.ForeignKey('userapp.Team', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.name;


class Team(models.Model):
    class Meta(object):
        verbose_name = '队伍'
        verbose_name_plural = '队伍'
    name = models.CharField('队伍名称', max_length=50, unique=True)
    english_name = models.CharField('英文队名', max_length=50)
    email = models.EmailField('队长邮箱', null=True, unique=True)
    phone_number = models.CharField('队长手机', max_length=11, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="用户")
    team_id = models.CharField('队伍ID', max_length=5, null=True)

    Liangxiang = 'LX'
    Zhongguancun = 'ZG'
    MATCH_ZONE = (
        (Liangxiang, '良乡校区'),
        (Zhongguancun, '中关村校区'),
    )
    match_zone = models.CharField('参赛地点', max_length=2, choices=MATCH_ZONE)

    def save(self, *args, **kwargs):
        # try:
        # print(self.email)
        self.user.username = self.email
        self.user.save()
        # except ObjectDoesNotExist:
        #     pass
        return super().save(*args, **kwargs)


    def __str__(self):
        return self.name


    def is_female_team(self):
        members = Person.objects.filter(team_belongto=self)
        if all([not member.is_male for member in members]):
            return True
        else:
            return False

    def is_new_student_team(self):
        members = Person.objects.filter(team_belongto=self)
        if all([member.grade == '1' for member in members]):
            return True
        else:
            return False

    def is_single_student_team(self):
        if len(Person.objects.filter(team_belongto=self)) == 1:
            return True
        else:
            return False

    def team_category(self):
        team_type = ""
        if self.is_female_team():
            team_type += '女队 '
        if self.is_new_student_team():
            team_type += '新生队'
        if not team_type:
            return '普通队伍'
        else:
            return team_type
    team_category.short_description = '队伍性质'

    def team_member_count(self):
        return len(Person.objects.filter(team_belongto=self))
    team_member_count.short_description = '队伍人数'

@receiver(post_delete, sender=Team)
def _mymodel_delete(sender, instance, **kwargs):
    instance.user.delete()

class Setting(models.Model):
    class Meta(object):
        verbose_name = '注册设置'
        verbose_name_plural = '注册设置'
    allow_to_modify = models.BooleanField('是否允许注册', default=True)
    team_limited_Liangxiang = models.IntegerField('良乡报名队伍数量限制', default=170)
    team_limited_Zhongguancun = models.IntegerField('中关村报名队伍数量限制', default=50)
    single_person_team_limited = models.IntegerField('单人队伍数量限制', default=15)

    def __str__(self):
        return '注册设置'

# if len(Setting.objects.all()) < 1:
#     Setting.objects.create()
