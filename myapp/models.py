from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, blank=True)

    def __str__(self):
        return self.user.username


class Fridge(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    humidity_min = models.FloatField()
    humidity_max = models.FloatField()

    def __str__(self):
        return f"Fridge: {self.name}, Location: {self.location}"


class TemperatureHumidityData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    fridge = models.ForeignKey(Fridge, on_delete=models.CASCADE)
    maintenance = models.BooleanField(default=False)

    def __str__(self):
        return f"Temperature: {self.temperature}, Humidity: {self.humidity}, Timestamp: {self.timestamp},id: {self.id}"

    def status_duration(self):
        # Calculer la durée depuis que les données ont été enregistrées
        now = timezone.now()
        delta = now - self.timestamp
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days} days, {hours} hours, {minutes} minutes"

    def status_duration_str(self):
        return str(self.status_duration())

    def save(self, *args, **kwargs):
        self.maintenance = self.maintenance
        super().save(*args, **kwargs)
