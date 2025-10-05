# food_analyzer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('log_meal/', views.log_meal_view, name='log_meal'),
    path('log_meal/confirm/', views.log_meal_confirm_view, name='log_meal_confirm'),
    path('api/get-nutrition/', views.get_nutrition_data_view, name='api_get_nutrition'),
]