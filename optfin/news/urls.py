from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_news, name='get_all_news'),
    path('create/', views.create_news, name='create_news'),
    path('<int:news_id>/update/', views.update_news, name='update_news'),
    path('<int:news_id>/', views.take_news, name='take_news'),
]