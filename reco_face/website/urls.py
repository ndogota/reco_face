from django.urls import path
from . import views

urlpatterns = [
    path('', views.image, name='image'),
    path('video/', views.video, name='video'),
    path('video/processing', views.processing, name='processing')
]
