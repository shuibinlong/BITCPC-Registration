from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import url
from django.http import HttpResponse

import csv

from .models import Person
from .models import Team
from .models import Setting

class PersonInLine(admin.TabularInline):
    model = Person

@staff_member_required
def export(request):
    GRADE = {
        '1': '大一',
        '2': '大二',
        '3': '大三',
        '4': '大四',
        '5': '研一',
        '6': '博一',
    }
    response = HttpResponse(content_type='text/csv', charset="gbk")
    response['Content-Disposition'] = 'attachment; filename="team.csv"'
    writer = csv.writer(response)

    all_teams = Team.objects.all()
    writer.writerow(['队伍序号', '队伍邮箱', '队伍名称', '队伍电话', '参赛地点', '队伍性质', '队伍人数', '队员1姓名', '队员1学号', '队员1性别', '队员1衣服尺码', '队员1年级', '队员1学院', '队员2姓名', '队员2学号', '队员2性别', '队员2衣服尺码', '队员2年级', '队员2学院', '队员3姓名', '队员3姓名', '队员3性别', '队员3衣服尺码', '队员3年级', '队员3学院'])

    for team in all_teams:
        team_field = []
        team_field.append(team.team_id)
        team_field.append(team.email)
        team_field.append(team.name)
        team_field.append(team.phone_number)
        # team_field.append(team.match_zone)
        team_field.append("中关村" if team.match_zone == 'ZG' else "良乡")
        team_field.append(team.team_category())
        team_field.append(team.team_member_count())

        members = Person.objects.filter(team_belongto=team)
        for member in members:
            team_field.append(member.name)
            team_field.append(member.student_id)
            team_field.append('男' if member.is_male else '女')
            team_field.append(member.clothing_size)
            team_field.append(GRADE[member.grade])
            team_field.append(member.institute)
        writer.writerow(team_field)
    return response

class TeamAdmin(admin.ModelAdmin):
    inlines = [
        PersonInLine,
    ]
    list_display = ('team_id', 'name', 'email', 'team_category', 'match_zone', 'team_member_count')
    list_filter = ('match_zone', )
    # change_list_template = 'admin/Team/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
                url(r"^export/$", export)
        ]
        return my_urls + urls
admin.site.register(Team, TeamAdmin)


class SettingAdmin(admin.ModelAdmin):
    model = Setting
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False if self.model.objects.count() > 0 else super().has_delete_permission(request)

admin.site.register(Setting, SettingAdmin)
