from django.urls import path
from . import views

urlpatterns = [
    path('chat/send/', views.send_message, name='send_message'),
]