from django.conf.urls import url, include 
from . import views

urlpatterns = [
    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.login, name='login'),
    url(r'^team/', views.team_get, name='team'),
    url(r'^team_post/', views.team_post, name='team_post'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^email/', views.email_verify, name='email'),
    url(r'^size/', views.size_table, name='size'),
]