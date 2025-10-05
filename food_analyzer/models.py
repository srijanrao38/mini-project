# food_analyzer/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    ACTIVITY_LEVEL_CHOICES = [
        (1.2, 'Sedentary'),
        (1.375, 'Lightly active'),
        (1.55, 'Moderately active'),
        (1.725, 'Very active'),
        (1.9, 'Super active'),
    ]
    activity_level = models.FloatField(choices=ACTIVITY_LEVEL_CHOICES, null=True, blank=True)
    GOAL_CHOICES = [('lose', 'Weight Loss'), ('maintain', 'Maintenance'), ('gain', 'Muscle Gain')]
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, null=True, blank=True)
    allergies = models.TextField(blank=True, help_text="Comma-separated, e.g., peanuts, shellfish")

    def __str__(self):
        return self.user.username

class Meal(models.Model):
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=20, choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner'), ('snack', 'Snack')], default='lunch')
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    tags = models.CharField(max_length=200, blank=True, help_text="e.g., vegetarian, gluten-free")
    recipe = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.meal_type})"

class DailyIntakeLog(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    food_name = models.CharField(max_length=100)
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.food_name} on {self.date}"