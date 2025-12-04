from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/refresh/', views.refresh_token, name='refresh_token'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.get_profile, name='get_profile'),
    path('auth/confirm/<str:token>/', views.confirm_email, name='confirm_email'),
    path('users/<int:user_id>/', views.get_or_update_user),
]
