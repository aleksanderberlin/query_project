from django import forms
import datetime
from django.core.exceptions import ValidationError
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'second_name', 'birthday', 'phone_number')
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'data-mask': '00.00.0000',
                                               'data-mask-clearifnotmatch': 'true'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '8 (000) 000-00-00',
                                                   'data-mask-clearifnotmatch': 'true'})
        }

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if (datetime.datetime.now() - datetime.datetime.combine(birthday, datetime.datetime.min.time())).days < 3650:
            raise ValidationError('Некорретная дата рождения')
        return birthday

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if isinstance(last_name, str):
            splitted_last_name = last_name.split(' ')
            for word in splitted_last_name:
                if not word.isalpha():
                    raise ValidationError('Некорретная фамилия')
            return last_name
        else:
            raise ValidationError('Некорретная фамилия')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        splitted_last_name = first_name.split(' ')
        for word in splitted_last_name:
            if not word.isalpha():
                raise ValidationError('Некорретное имя')
        return first_name

    def clean_second_name(self):
        second_name = self.cleaned_data['second_name']
        if isinstance(second_name, str):
            splitted_last_name = second_name.split(' ')
            for word in splitted_last_name:
                if not word.isalpha():
                    raise ValidationError('Некорретное имя')
            return second_name
        else:
            raise ValidationError('Некорретное имя')


class RequestFormUser(UserForm):
    CHOICES = [('university', 'Обучение в университете'),
               ('hostel', 'Проживание в общежитии')]

    type = forms.ChoiceField(choices=CHOICES, label='Тип обращения', widget=forms.RadioSelect())


class RequestFormSubjectHostel(forms.Form):
    REQUEST_CHOICES = [
        ('Оформление договора', 'Оформление договора'),
        ('Продление договора', 'Дополнительное соглашение о продлении договора'),
        ('Льгота', 'Оформление льготного проживания'),
        ('Смена Комнаты', 'Смена комнаты'),
        ('Расторжение договора', 'Расторжение договора'),
        ('Другое', 'Другое')
    ]

    question = forms.ChoiceField(choices=REQUEST_CHOICES, widget=forms.RadioSelect(),
                                 label='Тема обращения')
    hostel_privileges = forms.BooleanField(label='Имеете ли Вы льготы?', required=False,
                                           widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    other_text = forms.CharField(max_length=150, label='Другое', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'readonly': 'True'}))


class RequestFormSubjectUniversity(forms.Form):
    CHOICES = [
        ('Дополнительное соглашение о повышении стоимости', 'Дополнительное соглашение о повышении стоимости'),
        ('Образовательный кредит', 'Оплата обучения образовательным кредитом'),
        ('Материнский капитал', 'Оплата обучения из средств материнского капитала'),
        ('Возврат денежных средств', 'Возврат денежных средств'),
        ('Смена Заказчика', 'Изменение Заказчика в договоре'),
        ('Расторжение', 'Расторжение договора'),
        ('Обходной лист', 'Обходной лист'),
        ('Другое', 'Другое')
    ]

    question = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(),
                                 label='Тема обращения')

    other_text = forms.CharField(max_length=150, label='Другое', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'readonly': 'True'}))


class SearchUser(forms.Form):
    user_id = forms.IntegerField(label='Клиент', widget=forms.Select(attrs={'class': 'form-control', 'required': True}))
