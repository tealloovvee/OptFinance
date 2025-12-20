from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_portfolios, name='get_all_portfolios'),
    path('create/', views.create_portfolio, name='create_portfolio'),
    path('<int:portfolio_id>/', views.get_portfolio, name='get_portfolio'),
]

