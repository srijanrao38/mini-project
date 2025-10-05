# food_analyzer/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserProfileForm, ImageUploadForm, CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile, DailyIntakeLog
from .forms import UserProfileForm, ImageUploadForm
from . import planner_engine
from . import ml_utils
import datetime
from django.http import JsonResponse 

# --- No changes to home, register, login, logout, profile views ---

def home_view(request):
    return render(request, 'food_analyzer/home.html')

# food_analyzer/views.py

# ... other imports ...
# CHANGE THIS IMPORT
from django.contrib.auth.forms import AuthenticationForm 
# TO THIS (We need our new custom form)
from .forms import UserProfileForm, ImageUploadForm, CustomUserCreationForm
# ... other imports ...


# Find this function and make the change
def register_view(request):
    if request.method == 'POST':
        # USE OUR NEW CUSTOM FORM HERE
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        # AND HERE
        form = CustomUserCreationForm()
    return render(request, 'food_analyzer/register.html', {'form': form})

# ... the rest of your views.py file remains the same ...

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'food_analyzer/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'food_analyzer/profile.html', {'form': form})

@login_required
def dashboard_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if not all([profile.age, profile.weight_kg, profile.height_cm, profile.gender, profile.activity_level, profile.goal]):
        return redirect('profile')

    meal_plan_data = planner_engine.generate_meal_plan(profile)
    today = datetime.date.today()
    todays_logs = DailyIntakeLog.objects.filter(user_profile=profile, date=today)
    
    total_calories_today = sum(log.calories for log in todays_logs)
    total_protein_today = sum(log.protein_g for log in todays_logs)
    total_carbs_today = sum(log.carbs_g for log in todays_logs)
    total_fat_today = sum(log.fat_g for log in todays_logs)
    
    target_calories = meal_plan_data['target_calories']
    calories_percentage = (total_calories_today / target_calories * 100) if target_calories > 0 else 0
    calories_percentage_capped = min(calories_percentage, 100)

    context = {
        'meal_plan': meal_plan_data['plan'],
        'target_calories': meal_plan_data['target_calories'],
        'plan_calories': meal_plan_data['plan_calories'],
        'todays_logs': todays_logs,
        'total_calories_today': total_calories_today,
        'total_protein_today': total_protein_today,
        'total_carbs_today': total_carbs_today,
        'total_fat_today': total_fat_today,
        'calories_percentage': calories_percentage_capped,
    }
    return render(request, 'food_analyzer/dashboard.html', context)

@login_required
def log_meal_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            predicted_name, confidence, nutrition_info = ml_utils.handle_uploaded_image(image)
            request.session['nutrition_info'] = nutrition_info
            return redirect('log_meal_confirm')
    else:
        form = ImageUploadForm()
    return render(request, 'food_analyzer/log_meal.html', {'form': form})

# --- THIS IS THE UPDATED FUNCTION ---
@login_required
def log_meal_confirm_view(request):
    # Get the nutrition data from the session that we stored after the AI prediction
    session_nutrition = request.session.get('nutrition_info')
    if not session_nutrition:
        return redirect('log_meal')

    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, user=request.user)
        
        # Get the food name submitted by the user from the form
        corrected_name = request.POST.get('food_name')
        
        # Check if the user changed the name
        if corrected_name.lower() == session_nutrition['name'].lower():
            # If the name is the same, use the nutrition data we already have
            final_nutrition = session_nutrition
        else:
            # If the name is different, we MUST re-fetch nutrition data for the new name
            final_nutrition = ml_utils.get_nutrition_data(corrected_name)
        
        # Log the meal with the final (potentially corrected) nutrition data
        if final_nutrition:
            DailyIntakeLog.objects.create(
                user_profile=profile,
                food_name=final_nutrition['name'],
                calories=final_nutrition['calories'],
                protein_g=final_nutrition['protein_g'],
                carbs_g=final_nutrition['carbs_g'],
                fat_g=final_nutrition['fat_g'],
            )
        
        # Clean up the session and redirect to the dashboard
        del request.session['nutrition_info']
        return redirect('dashboard')

    return render(request, 'food_analyzer/log_meal_confirm.html', {'nutrition': session_nutrition})

@login_required
def get_nutrition_data_view(request):
    food_name = request.GET.get('food')
    if not food_name:
        return JsonResponse({'error': 'Food name not provided'}, status=400)
    
    nutrition_data = ml_utils.get_nutrition_data(food_name)
    
    if nutrition_data:
        return JsonResponse(nutrition_data)
    else:
        return JsonResponse({'error': 'Nutrition data not found'}, status=404)