from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from formtools.wizard.views import SessionWizardView
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout
import uuid
import datetime
from django.utils import timezone
import json

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
def specialist_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('specialist_login')