from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, TemperatureHumidityData


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email']


class CombinedForm(forms.ModelForm):
    class Meta:
        model = TemperatureHumidityData
        fields = ['fridgeName', 'fridgeLocation', 'temperatureMin', 'temperatureMax', 'humidityMin', 'humidityMax']

    fridgeName = forms.CharField(max_length=255)
    fridgeLocation = forms.CharField(max_length=255)
    temperatureMin = forms.FloatField()
    temperatureMax = forms.FloatField()
    humidityMin = forms.FloatField()
    humidityMax = forms.FloatField()
