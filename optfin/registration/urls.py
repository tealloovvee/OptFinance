from django.urls import path
from . import views

urlpatterns = [
    path('users/create/', views.create_user),
    path('users/<int:user_id>/', views.get_user),
    path('users/<int:user_id>/update/', views.update_user),
    path('users/<int:user_id>/delete/', views.delete_user),
]
