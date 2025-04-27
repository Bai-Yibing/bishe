from django.urls import path

from . import views

app_name = 'web'

urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'index/', views.index, name='index'),
    path('huizong', views.huizong, name='huizong'),
    # path('fenxi', views.fenxi, name='fenxi'),
    path('yuce', views.yuce, name='yuce'),
]
