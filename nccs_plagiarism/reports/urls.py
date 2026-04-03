from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_report, name='upload_report'),
    path('repository/', views.repository, name='repository'),
    path('compare/', views.compare_reports, name='compare_reports'),
    path('success/', views.upload_success, name='upload_success'),
]
