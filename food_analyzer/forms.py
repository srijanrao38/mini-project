# food_analyzer/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

# --- This is the NEW custom registration form ---
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a common CSS class to all fields for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'

# --- This is your existing form for the user profile ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user']

# --- This is your existing form for uploading images ---
class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label='Upload a Food Image',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )