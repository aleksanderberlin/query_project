from django import forms

from specialist.models import Specialist
from .models import Pretension


class PretensionForm(forms.ModelForm):
    SEXCHOICES = (
        ('M', 'Мужчина'),
        ('W', 'Женщина')
    )
    is_buyer_student_same = forms.BooleanField(label='Заказчик и Обучающийся одно и то же лицо',
                                               required=False, widget=forms.CheckboxInput())
    is_without_peni = forms.BooleanField(label='Без пени', required=False, widget=forms.CheckboxInput())

    other_text = forms.CharField(max_length=200, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'в связи с...',
                                                                'style': 'display: none;'}))
    another_vuz = forms.CharField(max_length=150, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control mb-2',
                                                                'placeholder': 'Название вуза...',
                                                                'style': 'display: none;'}))
    address_first_line = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())
    address_second_line = forms.CharField(max_length=150, required=False, widget=forms.HiddenInput())
    postal_code = forms.CharField(max_length=15, required=True, widget=forms.HiddenInput())
    buyer_sex = forms.ChoiceField(choices=SEXCHOICES,
                                  widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Пол'}))
    student_sex = forms.ChoiceField(choices=SEXCHOICES,
                                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Пол'}))

    class Meta:
        model = Pretension
        exclude = ('creator', 'pretension_file', )
        widgets = {
            'buyer_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'buyer_second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'buyer_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'student_first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'}),
            'student_second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'}),
            'student_last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер'}),
            'contract_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата',
                                                    'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}),
            'specialty': forms.Select(attrs={'class': 'form-control', 'placeholder': 'ОП', 'required': True}),
            'prikaz_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер'}),
            'prikaz_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата',
                                                    'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}),
            'otch_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата',
                                                    'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес'}),
            'debt_sum': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Сумма'}),
            'debt_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата возникновения',
                                                    'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}),
            'send_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Дата отправки',
                                                    'data-mask': '00.00.0000', 'data-mask-clearifnotmatch': 'true'}),
            'performer': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Исполнитель'}),
            'director': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Руководитель'}),
        }
