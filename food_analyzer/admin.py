# food_analyzer/admin.py
from django.contrib import admin
from .models import UserProfile, Meal, DailyIntakeLog

admin.site.register(UserProfile)
admin.site.register(Meal)
admin.site.register(DailyIntakeLog)