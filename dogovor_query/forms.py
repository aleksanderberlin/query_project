from django import forms
import datetime
from django.core.exceptions import ValidationError
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from .models import Specialist


# class CustomSpecialistCreationForm(UserCreationForm):
#     class Meta(UserCreationForm):
#         model = Specialist
#         fields = '__all__'
#
#
# class CustomSpecialistChangeForm(UserChangeForm):
#     class Meta:
#         model = Specialist
#         fields = '__all__'
#
#
# class LoginForm(forms.Form):
#     username = forms.CharField(label='Имя пользователя',
#                                widget=forms.TextInput(attrs={'class': 'form-control',
#                                                              'placeholder': 'Введите имя пользователя'}))
#     password = forms.CharField(label='Пароль',
#                                widget=forms.PasswordInput(attrs={'class': 'form-control',
#                                                                  'placeholder': 'Введите пароль'}))


class RequestFormUser(forms.Form):
    CHOICES = [('university', 'Обучение в университете'),
               ('hostel', 'Проживание в общежитии')]

    fio = forms.CharField(max_length=150, label='ФИО Обучающегося', widget=forms.TextInput(attrs={
        'class': 'form-control'}))
    birthday = forms.DateField(label='Дата рождения', widget=forms.DateInput(attrs={
        'class': 'form-control', 'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}))
    phone_number = forms.CharField(max_length=17, label='Номер телефона', widget=forms.TextInput(attrs={
        'class': 'form-control', 'data-mask': '8 (000) 000-00-00', 'data-mask-clearifnotmatch': 'true'}))
    type = forms.ChoiceField(choices=CHOICES, label='Тип обращения', widget=forms.Select(attrs={
        'class': 'form-control'}))
    user_uid = forms.CharField(max_length=40, widget=forms.HiddenInput())

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if (datetime.datetime.now() - datetime.datetime.combine(birthday, datetime.datetime.min.time())).days < 3650:
            raise ValidationError('Некорретная дата рождения')
        return birthday

    def clean_fio(self):
        fio = self.cleaned_data['fio']
        splitted_fio = fio.split(' ')
        for word in splitted_fio:
            if not word.isalpha():
                raise ValidationError('Некорретное ФИО')
        if len(splitted_fio) < 2:
            raise ValidationError('Некорретное ФИО')
        return fio


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
    hostel_privileges = forms.CharField(max_length=150, label='Льготы', widget=forms.TextInput(attrs={
        'class': 'form-control'}), required=False)
    temporary_move = forms.BooleanField(label='Выезжали ли Вы на временный выезд из общежития?', required=False,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    other_text = forms.CharField(max_length=150, label='Другое', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'readonly': 'True'}))


class RequestFormSubjectHostelMove(forms.Form):
    hostel_date_moveout = forms.DateField(label='Дата выезда из общежития', widget=forms.DateInput(attrs={
        'class': 'form-control', 'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}))
    hostel_date_movein = forms.DateField(label='Дата возврата в общежитие', widget=forms.DateInput(attrs={
        'class': 'form-control', 'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}))


class RequestFormSubjectUniversity(forms.Form):
    CHOICES = [
        ('Дополнительное соглашение о повышении стоимости', 'Дополнительное соглашение о повышении стоимости'),
        ('Образовательный кредит', 'Оплата обучения образовательным кредитом'),
        ('Материнский капитал', 'Оплата обучения из средств материнского капитала'),
        ('Возврат денежных средств', 'Возврат денежных средств'),
        ('Смена Заказчика', 'Изменение Заказчика в договоре'),
        ('Расторжение', 'Расторжение договора'),
        ('Другое', 'Другое')
    ]

    question = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(),
                                         label='Тема обращения')

    other_text = forms.CharField(max_length=150, label='Другое', required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'readonly': 'True'}))
