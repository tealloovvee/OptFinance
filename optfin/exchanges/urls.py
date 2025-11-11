from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_exchanges, name='get_all_exchanges'),
    path('<int:exchange_id>/', views.get_exchange, name='get_exchange'),
]