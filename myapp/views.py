import serial
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from myapp.models import TemperatureHumidityData, UserProfile, Fridge
from .forms import SignUpForm, UserProfileForm, CombinedForm


def signIn(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me', False)

        # Vérifier si l'utilisateur existe dans le modèle UserProfile
        try:
            user_profile = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            messages.error(request, 'L\'utilisateur n\'existe pas.')
            return render(request, 'sign-in.html')

        # Utiliser l'authentification Django
        user = authenticate(request, username=user_profile.user.username, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            return redirect('dashboard')  # Assurez-vous que le nom de la vue est correct
        else:
            messages.error(request, 'Identifiants incorrects.')

    return render(request, 'sign-in.html')


def signOut(request):
    # Use the LogoutView provided by Django
    response = LogoutView.as_view(next_page='dashboard')(request)  # Redirect the user after logout
    return response


def signUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Authentifier l'utilisateur
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']
            user = authenticate(username=username, password=raw_password)

            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully signed up and logged in.')
                return redirect('dashboard')  # Rediriger vers la vue du tableau de bord après l'inscription
            else:
                messages.error(request, 'Failed to authenticate user.')
        else:
            messages.error(request, 'Form validation failed. Please check the errors below.')
    else:
        form = SignUpForm()
        profile_form = UserProfileForm()

    return render(request, 'sign-up.html', {'form': form, 'profile_form': profile_form})


@login_required(login_url='signIn')
def dashboard(request):
    # Récupérer les données à afficher dans le tableau de bord depuis la base de données ou d'autres sources
    temperature_humidity_data = TemperatureHumidityData.objects.all()

    # Inclure les données dans le contexte de rendu
    context = {
        'temperature_humidity_data': temperature_humidity_data
    }

    # Rendre le template "dashboard.html" avec les données incluses dans le contexte
    return render(request, 'dashboard.html', context)


def profile(request):
    return render(request, 'profile.html')


def rtl(request):
    return render(request, 'rtl.html')


def tables(request):
    # Récupérer toutes les données depuis la base de données
    temperature_humidity_data = TemperatureHumidityData.objects.all().order_by('-timestamp')

    # Configurer la pagination
    paginator = Paginator(temperature_humidity_data, 10)  # 10 éléments par page

    # Récupérer le numéro de la page demandée
    page = request.GET.get('page')

    try:
        # Récupérer les données pour la page spécifiée
        temperature_humidity_data = paginator.page(page)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, récupérer la première page
        temperature_humidity_data = paginator.page(1)
    except EmptyPage:
        # Si la page est out of range, récupérer la dernière page
        temperature_humidity_data = paginator.page(paginator.num_pages)

    # Inclure les données paginées dans le contexte
    context = {
        'temperature_humidity_data': temperature_humidity_data
    }

    # Rendre le template "tables.html" avec les données paginées incluses dans le contexte
    return render(request, 'tables.html', context)


def get_all_data(request):
    # Récupérer toutes les données depuis la base de données
    all_data = TemperatureHumidityData.objects.all().order_by('-timestamp')

    serialized_data = [
        {
            'id': entry.id,
            'temperature': entry.temperature,
            'humidity': entry.humidity,
            'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status_duration': entry.status_duration_str(),  # Appel de la méthode pour obtenir la durée
        }
        for entry in all_data
    ]

    return JsonResponse({'results': serialized_data})


def VR(request):
    # Fetch the latest temperature data
    latest_data = TemperatureHumidityData.objects.latest('timestamp')

    # Get the temperature value
    temperature = latest_data.temperature
    humidity = latest_data.humidity

    # Determine the weather state based on temperature range
    if temperature < -10:
        weather_state = 'Extremely cold'
    elif -10 <= temperature < 5:
        weather_state = 'Very cold'
    elif 5 <= temperature < 15:
        weather_state = 'Temperate'
    elif 15 <= temperature < 25:
        weather_state = 'Hot'
    elif temperature >= 25:
        weather_state = 'Very hot'
    else:
        weather_state = 'Extremely hot'

    # Pass the temperature and weather state to the template
    context = {
        'temperature': temperature,
        'weather_state': weather_state,
        'humidity': humidity
    }
    return render(request, 'virtual-reality.html', context)


def api(request):
    return render(request, 'partials/__api.html')


def getData(request):
    # Configuration du port série
    ser = serial.Serial('COM4', 115200)  # Assurez-vous de spécifier le bon port

    # Lecture des données série
    arduino_data = ser.readline().decode('latin-1').strip()

    temperature, humidity = arduino_data.split(',')

    # Fermer la connexion série
    ser.close()

    # Remplacez 'nom_du_fridge' par le nom du frigo spécifique à associer
    fridge_instance = Fridge.objects.get(name='fridge1')

    # Créer une instance de TemperatureHumidityData associée au frigo
    temperature_humidity_data = TemperatureHumidityData.objects.create(
        temperature=temperature,
        humidity=humidity,
        fridge=fridge_instance
    )

    temperature_humidity_data = TemperatureHumidityData.objects.all()

    context = {
        'temperature_humidity_data': temperature_humidity_data
    }

    return render(request, 'arduinoData.html', context)


def fridges(request):
    # Obtenez toutes les instances de TemperatureHumidityData associées au fridge1
    fridge1_data = TemperatureHumidityData.objects.filter(fridge__name='fridge1')

    # Calculer la moyenne des températures
    average_temperature = fridge1_data.aggregate(Avg('temperature'))['temperature__avg']
    average_humidity = fridge1_data.aggregate(Avg('humidity'))['humidity__avg']

    # Vérifier si les moyennes ne sont pas None avant d'arrondir
    if average_temperature is not None:
        average_temperature = round(average_temperature, 2)

    if average_humidity is not None:
        average_humidity = round(average_humidity, 2)

    # Autres données relatives aux frigos
    fridges_data = Fridge.objects.all()

    context = {
        'fridges_data': fridges_data,
        'average_temperature': average_temperature,
        'average_humidity': average_humidity,
    }

    return render(request, 'Fridges.html', context)


def add_fridge(request):
    if request.method == 'POST':
        form = CombinedForm(request.POST)
        if form.is_valid():
            # Create Fridge instance
            fridge = Fridge.objects.create(
                name=form.cleaned_data['fridgeName'],
                location=form.cleaned_data['fridgeLocation'],
                temperature_min=form.cleaned_data['temperatureMin'],
                temperature_max=form.cleaned_data['temperatureMax'],
                humidity_min=form.cleaned_data['humidityMin'],
                humidity_max=form.cleaned_data['humidityMax']
            )

            # Create TemperatureHumidityData instance
            temperature_humidity_data = form.save(commit=False)
            temperature_humidity_data.fridge = fridge
            temperature_humidity_data.temperature = 0  # Set default value or adjust as needed
            temperature_humidity_data.humidity = 0  # Set default value or adjust as needed
            temperature_humidity_data.save()

            return redirect('fridges')  # Redirect to your desired page after successful form submission
    else:
        form = CombinedForm()

    return render(request, 'partials/__FridgeForm.html', {'form': form})


def update_maintenance(request, data_id):
  data = get_object_or_404(TemperatureHumidityData, id=data_id)
  data.maintenance = request.POST.get('maintenance') == '1'
  data.save()
  return JsonResponse({'success': True})
