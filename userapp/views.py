from collections import namedtuple
from functools import wraps
from hashlib import sha1

from django.contrib.auth import authenticate
from django.contrib.auth import login as login_as
from django.contrib.auth import logout as logout_as
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import HttpResponse, redirect, render
from django.urls import reverse_lazy

import register_system.settings
from homepage.models import HomePage
from userapp.models import Person, Setting, Team

MEMBER_LIMIT = 3


def team_number_lx(): return len(Team.objects.filter(match_zone='LX'))


def team_number_zg(): return len(Team.objects.filter(match_zone='ZG'))


def team_number_single(): return len(
    [x for x in Team.objects.all() if x.is_new_student_team()])


def calc_email(email):
    inputs = (email + register_system.settings.SECRET_KEY).encode()
    result = sha1(inputs).hexdigest()[:6]
    return result


def allow_register(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        allow_modify = True
        try:
            setting = Setting.objects.get(pk=1)
            allow_modify = setting.allow_to_modify
        except DoesNotExist:
            pass

        if allow_modify:
            return func(*args, **kwargs)
        else:
            context = {
                'message': '已停止注册。',
                'redirect_url': '/',
            }
            kwargs['context'] = context
            kwargs['template_name'] = 'userapp/message.html'
            return render(*args, **kwargs)
    return wrapper


@allow_register
def register(request):
    context = {
        'homepage': HomePage.objects.get(pk=1),
        'max_member': MEMBER_LIMIT,
        'setting': Setting.objects.get(pk=1),
        'team_number_lx': team_number_lx(),
        'team_number_zg': team_number_zg(),
    }
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(reverse_lazy('team'))
        else:
            return render(request, 'userapp/register.html', context)

    if request.method == 'POST':
        captain_email = request.POST.get('captain-email', '')
        team_name = request.POST.get('team-name', '')
        password = request.POST.get('password', '')
        captain_phone = request.POST.get('captain-phone', '')
        match_zone = request.POST.get('match-zone', '')
        verify_code = request.POST.get('verify-code', '')

        # if verify_code != calc_email(captain_email):
        #     return HttpResponse('邮件验证失败。')

        if not (captain_email and team_name and password and captain_phone and match_zone):
            return HttpResponse('存在字段为空，注册失败。')

        member_info = []
        Member = namedtuple(
            'Member', ['id', 'name', 'gender', 'clothing_size', 'grade', 'institute'])
        for index in range(MEMBER_LIMIT):
            student_id = request.POST.get('student-id-' + str(index), '')
            student_name = request.POST.get('student-name-' + str(index), '')
            student_gender = request.POST.get('gender-' + str(index), '')
            clothing_size = request.POST.get('clothing-size-' + str(index), '')
            student_grade = request.POST.get('grade-' + str(index), '')
            institute = request.POST.get('institute-' + str(index), '')
            if Person.objects.filter(student_id=student_id):
                return render(request, 'userapp/message.html', {'message': '学生重复报名。', 'redirect_url': reverse_lazy('register')})
            member_info.append(Member(
                student_id, student_name, student_gender, clothing_size, student_grade, institute))
        if not member_info[0].id:
            return HttpResponse('未添加队员信息。')

        context = {}
        user = None
        with transaction.atomic():

            # check team requirements
            team_limit_lx = Setting.objects.get(pk=1).team_limited_Liangxiang
            team_limit_zg = Setting.objects.get(pk=1).team_limited_Zhongguancun
            team_limit_single = Setting.objects.get(
                pk=1).single_person_team_limited

            if team_number_lx() > team_limit_lx:
                return render(request, 'userapp/message.html', {'message': '良乡队伍已满。', 'redirect_url': reverse_lazy('register')})
            if team_number_zg() > team_limit_zg:
                return render(request, 'userapp/message.html', {'message': '中关村队伍已满。', 'redirect_url': reverse_lazy('register')})
            if team_number_single() > team_limit_single:
                return render(request, 'userapp/message.html', {'message': '单人队伍已满。', 'redirect_url': reverse_lazy('register')})

            team_id = 'L' if match_zone == 'LX' else 'Z'

            def find_min_id():
                for i in range(2**32):
                    if not Team.objects.filter(team_id=team_id+str(i)):
                        return i

            team_id += str(find_min_id())
            if Team.objects.filter(name=team_name):
                return render(request, 'userapp/message.html', {'message': '存在相同的队伍名称。', 'redirect_url': reverse_lazy('register')})
            if Team.objects.filter(email=captain_email):
                return render(request, 'userapp/message.html', {'message': '已注册的邮箱。', 'redirect_url': reverse_lazy('register')})

            user = User.objects.create_user(
                captain_email, captain_email, password)
            team = Team.objects.create(name=team_name, email=captain_email,
                                       phone_number=captain_phone, user=user, match_zone=match_zone, team_id=team_id)
            for member in member_info:
                if member.id:
                    Person.objects.create(name=member.name, student_id=member.id, clothing_size=member.clothing_size,
                                          is_male=True if member.gender == 'male' else False,
                                          grade=member.grade, institute=member.institute,
                                          team_belongto=team)

            context = {
                'message': '注册成功, 你的队伍ID是 "' + team_id + '" 。',
            }
        login_as(request, user)
        return render(request, 'userapp/message.html', context)

    else:
        return HttpResponse('Not Implemented')


def login(request):
    context = {
        'homepage': HomePage.objects.get(pk=1),
    }
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(reverse_lazy('team'))
        else:
            return render(request, 'userapp/login.html', context)
    if request.method == 'POST':
        email = request.POST.get('captain-email', '')
        password = request.POST.get('password', '')
        if not (email and password):
            return HttpResponse('请输入用户名和密码。')

        user = authenticate(username=email, password=password)
        if user is not None:
            login_as(request, user)
            context = {
                'homepage': HomePage.objects.get(pk=1),
            }
            return redirect(reverse_lazy('team'))
        else:
            return HttpResponse('用户名和密码错误。')
    else:
        return HttpResponse('Not Implemented')


@login_required(login_url=reverse_lazy('login'))
def team_get(request):
    username = request.user.get_username()
    if request.method == "GET":
        if username == "admin":
            return redirect('/admin')
        team = Team.objects.get(email=username)
        members = Person.objects.filter(team_belongto=team)

        context = {
            'homepage': HomePage.objects.get(pk=1),
            'team': team,
            'members': members,
            'max_member': MEMBER_LIMIT,
        }
        return render(request, 'userapp/team.html', context)


@allow_register
@login_required(login_url=reverse_lazy('login'))
def team_post(request):
    username = request.user.get_username()
    if request.method == 'POST':
        password = request.POST.get("password", "")
        password_veri = request.POST.get("password_veri", "")

        user = User.objects.get(username=username)
        team = Team.objects.get(email=username)
        if password and password == password_veri:
            user.set_password(password)
        
        team_name = request.POST.get("team-name", "")
        if team_name:
            team.name = team_name

        captain_phone = request.POST.get("captain-phone", "")
        if captain_phone:
            team.phone_number = captain_phone

        # not allowed to modify the match zone
        # match_zone = request.POST.get("match-zone", "")
        # if match_zone:
        #     team.match_zone = match_zone

        member_info = []
        Member = namedtuple(
            'Member', ['id', 'name', 'gender', 'clothing_size', 'grade', 'institute'])
        for index in range(MEMBER_LIMIT):
            student_id = request.POST.get('student-id-' + str(index), '')
            student_name = request.POST.get('student-name-' + str(index), '')
            student_gender = request.POST.get('gender-' + str(index), '')
            clothing_size = request.POST.get('clothing-size-' + str(index), '')
            student_grade = request.POST.get('grade-' + str(index), '')
            institute = request.POST.get('institute-' + str(index), '')
            member_info.append(Member(
                student_id, student_name, student_gender, clothing_size, student_grade, institute))

        with transaction.atomic():
            members = Person.objects.filter(team_belongto=team)

            if member_info[0].id:
                for member in members:
                    member.delete()

            for member in member_info:
                if member.id:
                    Person.objects.create(name=member.name, student_id=member.id, clothing_size=member.clothing_size,
                                          is_male=True if member.gender == 'male' else False,
                                          grade=member.grade, institute=member.institute,
                                          team_belongto=team)
            team.save()
        return redirect(reverse_lazy('team'))


def logout(request):
    logout_as(request)
    return redirect('/')


@allow_register
def email_verify(request):

    def validateEmail(email):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    email = request.POST.get('email', '')
    # raise EnvironmentError()
    # print('email:' + email)
    result = calc_email(email)
    if not validateEmail(email):
        return HttpResponse('failed')

    send_mail('比赛邮箱验证码', '你的比赛邮箱验证码为： ' + result,
              from_email=register_system.settings.EMAIL_HOST_USER,
              recipient_list=[email],
              )
    return HttpResponse('success')


def size_table(request): 
    return render(request, 'userapp/size_table.html')
