from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

# Create your views here.
from .forms import *
from constance import config
from django.contrib import messages


@permission_required('database.change_server_settings')
def server_settings(request):
    if request.method == 'POST':
        settings_form = ServerSettingsForm(request.POST)
        if settings_form.is_valid():
            config.EXCLUDE_WEEKDAYS = settings_form.cleaned_data['exclude_weekdays']
            config.TIME_OPENING = settings_form.cleaned_data['time_opening']
            config.TIME_CLOSING = settings_form.cleaned_data['time_closing']
            messages.SUCCESS('Изменения успешно сохранены')
        else:
            messages.ERROR('Введенные параметры некорректны.')
    settings_form = ServerSettingsForm(initial={'exclude_weekdays': config.EXCLUDE_WEEKDAYS,
                                                'time_opening': config.TIME_OPENING,
                                                'time_closing': config.TIME_CLOSING})
    return render(request, 'server/server_settings.html', {'server_settings_form': settings_form})
