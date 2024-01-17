from django.contrib import admin
from .models import TemperatureHumidityData, UserProfile, Fridge

admin.site.register(TemperatureHumidityData)
admin.site.register(UserProfile)
admin.site.register(Fridge)
