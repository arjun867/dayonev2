from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    
    NATIONALITY_CHOICES = [
        ('indian', 'Indian'),
        ('non-indian', 'Non-Indian'),
    ]
    nationality = forms.ChoiceField(choices=NATIONALITY_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'nationality', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
