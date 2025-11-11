from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_cryptocurrencies, name='get_all_cryptocurrencies'),
    path('<int:coin_id>/', views.get_crypto_coin, name='get_crypto_coin'),
]