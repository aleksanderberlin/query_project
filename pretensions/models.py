from django.db import models
from django.conf import settings
from django.utils import timezone


class KeyRate(models.Model):
    key_rate = models.FloatField(verbose_name='Ключевая ставка')
    peni_part_key_rate = models.CharField(max_length=15, verbose_name='Доля ключевой ставки', default='1/300')
    start_date = models.DateField(verbose_name='Начало')
    end_date = models.DateField(verbose_name='Конец', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    def is_actual(self):
        if self.end_date is None:
            return True
        elif self.end_date > timezone.now().date():
            return True
        else:
            return False

    def part_key_rate_to_float(self):
        if '/' in self.peni_part_key_rate:
            if len(self.peni_part_key_rate.split('/')) == 2:
                a, b = self.peni_part_key_rate.split('/')
                return int(a) / int(b)
        return None


class Specialty(models.Model):
    spec_code = models.CharField(max_length=10, verbose_name='Код специальности')
    spec_name = models.CharField(max_length=100, verbose_name='Наименование специальности')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    def __str__(self):
        return self.spec_code + ' ' + self.spec_name


class Performer(models.Model):
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    second_name = models.CharField(max_length=50, verbose_name='Отчество')
    position = models.CharField(max_length=150, verbose_name='Должность')
    phone_number = models.CharField(max_length=11, verbose_name='Номер телефона')
    is_default = models.BooleanField(verbose_name='По умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    def __str__(self):
        if self.second_name:
            return self.last_name + ' ' + self.first_name + ' ' + self.second_name
        else:
            return self.last_name + ' ' + self.first_name


class Director(models.Model):
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    second_name = models.CharField(max_length=50, verbose_name='Отчество', blank=True, null=True)
    position = models.CharField(max_length=150, verbose_name='Должность')
    is_default = models.BooleanField(verbose_name='По умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    def __str__(self):
        if self.second_name:
            return self.last_name + ' ' + self.first_name + ' ' + self.second_name
        else:
            return self.last_name + ' ' + self.first_name

    def get_sign_name(self):
        if self.second_name:
            return self.first_name[0] + '. ' + self.second_name[0] + '. ' + self.last_name
        else:
            return self.first_name[0] + '. ' + self.last_name


class Pretension(models.Model):
    class OtchReason(models.TextChoices):
        INITIATIVE = 'initiative', 'Инициатива Обучающегося'
        ACADEMIC_DEBT = 'academic_debt', 'Академическая неуспеваемость'
        MONEY_DEBT = 'money_debt', 'Задолженность по оплате'
        VUZ_CHANGE = 'vuz_change', 'Перевод в другой вуз'
        OTHER = 'other', 'Другое'

    buyer_first_name = models.CharField(max_length=50, verbose_name='Фамилия Заказчика')
    buyer_second_name = models.CharField(max_length=50, verbose_name='Имя Заказчика', blank=True, null=True)
    buyer_last_name = models.CharField(max_length=50, verbose_name='Отчество Заказчика')
    student_first_name = models.CharField(max_length=50, verbose_name='Фамилия Обучающегося', blank=True, null=True)
    student_second_name = models.CharField(max_length=50, verbose_name='Имя Обучающегося', blank=True, null=True)
    student_last_name = models.CharField(max_length=50, verbose_name='Отчество Обучающегося', blank=True, null=True)
    prikaz_number = models.CharField(max_length=15, verbose_name='Номер приказа')
    prikaz_date = models.DateField(verbose_name='Дата приказа')
    otch_date = models.DateField(verbose_name='Дата отчисления')
    otch_reason = models.CharField(max_length=30, verbose_name='Причина отчисления', choices=OtchReason.choices,
                                   default=OtchReason.choices[0])
    contract_number = models.CharField(max_length=20, verbose_name='Номер договора')
    contract_date = models.DateField(verbose_name='Дата договора')
    specialty = models.ForeignKey(Specialty, on_delete=models.RESTRICT, verbose_name='Специальность',
                                  default=Specialty.objects.all().first().pk)
    address = models.CharField(max_length=300, verbose_name='Адрес')
    debt_sum = models.FloatField(verbose_name='Сумма задолженности')
    debt_date = models.DateField(verbose_name='Дата возникновения задолженности')
    send_date = models.DateField(verbose_name='Дата отправки')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, verbose_name='Создатель',
                                blank=True, null=True)
    performer = models.ForeignKey(Performer, on_delete=models.RESTRICT, verbose_name='Исполнитель',
                                  default=Performer.objects.filter(is_default=True).first().pk)
    director = models.ForeignKey(Director, on_delete=models.RESTRICT, verbose_name='Руководитель',
                                 default=Director.objects.filter(is_default=True).first().pk)
    pretension_file = models.FilePathField(verbose_name='Путь к файлу')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    class Meta:
        permissions = [
            ('create_pretension', 'Создавать претензии'),
        ]
