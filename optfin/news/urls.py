from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_or_create_news, name='get_or_create_news'),
    path('<int:news_id>/', views.get_or_update_news, name='get_or_update_news'),
]