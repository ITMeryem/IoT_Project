from django.urls import path
from .views import signUp, dashboard, profile, rtl, VR, api, signIn, signOut, fridges, \
    add_fridge, get_all_data, update_maintenance, getData, tables

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('signIn', signIn, name='signIn'),
    path('arduinoData', getData, name='arduinoData'),
    path('signUp', signUp, name='signUp'),
    path('profile', profile, name='profile'),
    path('rtl', rtl, name='rtl'),
    path('tables', tables, name='tables'),
    path('', VR, name='VR'),
    path('api', api, name='api'),
    path('signOut', signOut, name='signOut'),
    path('fridges', fridges, name='fridges'),
    path('add_fridge', add_fridge, name='add_fridge'),
    path('tables/all/', get_all_data, name='get_all_data'),
    path('tables/update_maintenance/<int:data_id>/', update_maintenance, name='update_maintenance'),

]
