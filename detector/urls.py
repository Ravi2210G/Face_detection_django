from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('live/', views.live, name='live'),       # Live webcam page
    path('live-feed/', views.live_feed, name='live-feed'),  # Video stream
]

