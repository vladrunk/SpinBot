from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_bot_view, name='start_bot'),
    path('stop/', views.stop_bot_view, name='stop_bot'),
]
