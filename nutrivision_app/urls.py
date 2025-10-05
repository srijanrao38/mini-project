# nutrivision_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('food_analyzer.urls')), # This will handle all app-related URLs
]