from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.


def specialist_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.GET:
                        return redirect(request.GET['next'])
                    else:
                        return redirect('query_list')
                else:
                    form = LoginForm(request.POST)
                    return render(request, 'specialist/login.html', {'form': form})
            else:
                form = LoginForm(request.POST)
                return render(request, 'specialist/login.html', {'form': form})
    else:
        if request.user.is_authenticated:
            return redirect('query_list')
        else:
            form = LoginForm()
            return render(request, 'specialist/login.html', {'form': form})


@login_required(login_url='specialist_login')
def specialist_settings(request):
    if request.method == 'POST':
        settings_form = SettingsForm(request.POST, instance=request.user)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'Изменения успешно сохранены.')
        else:
            messages.error(request, 'Указанный номер стола занят другим специалистом. Изменения не сохранены.')

    else:
        settings_form = SettingsForm(instance=request.user)
    return render(request, 'specialist/settings.html', {'settings_form': settings_form})


@login_required(login_url='specialist_login')
def specialist_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('specialist_login')
