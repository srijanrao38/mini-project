# food_analyzer/planner_engine.py
from .models import UserProfile, Meal
import random

def calculate_tdee(profile: UserProfile):
    if not all([profile.gender, profile.weight_kg, profile.height_cm, profile.age, profile.activity_level]):
        return 2000 # Return a default value if profile is incomplete

    if profile.gender == 'M':
        bmr = 88.362 + (13.397 * profile.weight_kg) + (4.799 * profile.height_cm) - (5.677 * profile.age)
    else: # 'F'
        bmr = 447.593 + (9.247 * profile.weight_kg) + (3.098 * profile.height_cm) - (4.330 * profile.age)
    
    tdee = bmr * profile.activity_level
    
    if profile.goal == 'lose':
        return tdee - 500
    elif profile.goal == 'gain':
        return tdee + 500
    else:
        return tdee

def generate_meal_plan(profile: UserProfile):
    target_calories = calculate_tdee(profile)
    
    # Filter meals based on user allergies
    user_allergies = [allergy.strip().lower() for allergy in profile.allergies.split(',') if allergy.strip()]
    
    all_meals = Meal.objects.all()
    
    # Exclude meals containing allergens in their name or tags
    safe_meals = []
    for meal in all_meals:
        is_safe = True
        for allergy in user_allergies:
            if allergy in meal.name.lower() or allergy in meal.tags.lower():
                is_safe = False
                break
        if is_safe:
            safe_meals.append(meal)

    # Simple meal selection logic (can be made much smarter later)
    plan = {
        'breakfast': random.choice([m for m in safe_meals if m.meal_type == 'breakfast']) if any(m.meal_type == 'breakfast' for m in safe_meals) else None,
        'lunch': random.choice([m for m in safe_meals if m.meal_type == 'lunch']) if any(m.meal_type == 'lunch' for m in safe_meals) else None,
        'dinner': random.choice([m for m in safe_meals if m.meal_type == 'dinner']) if any(m.meal_type == 'dinner' for m in safe_meals) else None,
    }
    
    # Calculate total calories of the generated plan
    total_calories = 0
    for meal in plan.values():
        if meal:
            total_calories += meal.calories
            
    return {'plan': plan, 'target_calories': target_calories, 'plan_calories': total_calories}