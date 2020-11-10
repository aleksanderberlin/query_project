from django import forms


class ServerSettingsForm(forms.Form):
    WEEKDAYS = [
        ("monday", "Понедельник"), ("tuesday", "Вторник"), ("wednesday", "Среда"),
        ("thursday", "Четверг"), ("friday", "Пятница"), ('saturday', 'Суббота'), ("sunday", "Воскресенье")
    ]
    exclude_weekdays = forms.MultipleChoiceField(choices=WEEKDAYS, label='Неприемные дни', required=False,
                                                 widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    time_opening = forms.TimeField(label='Время начала приема', widget=forms.TextInput(attrs={'class': 'form-control'}))
    time_closing = forms.TimeField(label='Время конца приема', widget=forms.TextInput(attrs={'class': 'form-control'}))
    time_break_start = forms.TimeField(label='Время начала перерыва',
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    time_break_end = forms.TimeField(label='Время конца перерыва',
                                     widget=forms.TextInput(attrs={'class': 'form-control'}))
