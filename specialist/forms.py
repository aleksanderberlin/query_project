from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Specialist


class CustomSpecialistCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = Specialist
        fields = '__all__'


class CustomSpecialistChangeForm(UserChangeForm):
    class Meta:
        model = Specialist
        fields = '__all__'


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя',
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Введите имя пользователя'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Введите пароль'}))


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Specialist
        fields = ['first_name', 'last_name', 'room', 'table_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя', 'required': 'True'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия', 'required': 'True'}),
            'room': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Кабинет', 'required': 'True'}),
            'table_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер стола',
                                                   'required': 'True'}),
        }