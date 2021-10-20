from django.conf.urls import url, include 
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^notice/(?P<notice_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^contact_us$', views.contact_us, name='contact_us'),
]