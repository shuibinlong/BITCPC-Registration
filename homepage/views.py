from django.shortcuts import render
from django.http import HttpResponse

from .models import Notice
from .models import HomePage
from .models import HomePageImage
from .models import NoticeFile

def index(request):
    latest_notice_list = Notice.objects.order_by('-pub_date')
    context = {
        'latest_notice_list': latest_notice_list,
        'homepage': HomePage.objects.get(pk=1),
        'top_title': HomePage.objects.get(pk=1).title.replace('<br>', ''),
        'slide_images': HomePageImage.objects.all(),
    }
    return render(request, 'homepage/index.html', context)

def detail(request, notice_id):
    notice = Notice.objects.get(pk=notice_id)
    files = NoticeFile.objects.filter(
        notice = notice
    )
    for file in files:
        filename = file.file.name
        filename = filename.lstrip('file/')
        setattr(file, 'filename', filename)
    context = {
        'notice': notice,
        'homepage': HomePage.objects.get(pk=1),
        'files': files,
    }
    return render(request, 'homepage/notice_detail.html', context)

def contact_us(request):
    context = {
        'homepage': HomePage.objects.get(pk=1),
    }
    return render(request, 'homepage/contact_us.html', context)
