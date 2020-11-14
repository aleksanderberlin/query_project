from django.db import models
from django.conf import settings
import uuid


class User(models.Model):
    user_uid = models.UUIDField(primary_key=False, default=uuid.uuid4, verbose_name='Идентификатор')
    first_name = models.CharField(max_length=40, verbose_name='Имя')
    second_name = models.CharField(max_length=40, verbose_name='Отчество', null=True, blank=True)
    last_name = models.CharField(max_length=40, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=17, verbose_name='Номер телефона')
    birthday = models.DateField(verbose_name='Дата рождения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    def __str__(self):
        if self.second_name:
            return self.last_name + ' ' + self.first_name + ' ' + self.second_name
        else:
            return self.last_name + ' ' + self.first_name

    class Meta:
        permissions = [
            ('search_requests', 'Искать по пользователям')
        ]
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Request(models.Model):
    class RequestTypes(models.TextChoices):
        UNIVERSITY = 'university', 'Университет'
        HOSTEL = 'hostel', 'Общежития'

    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    number = models.IntegerField(verbose_name='Номер')
    type = models.CharField(max_length=10, verbose_name='Тип', choices=RequestTypes.choices)
    question = models.CharField(max_length=250, verbose_name='Тема')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        permissions = [
            ('view_query', 'Смотреть список новых заявок'),
            ('create_reports', 'Формировать отчеты'),
            ('work_requests', 'Принимать клиентов'),
            ('view_dashboard', 'Смотреть дэшбоард')
        ]

    def __str__(self):
        return str(self.pk) + ' Заявка [' + self.type + '] - ' + self.created_at.strftime('%d.%m.%Y %H:%M')

    def get_query_number(self):
        if self.type == 'university':
            prefix = 'У-'
        elif self.type == 'hostel':
            prefix = 'ОБ-'
        else:
            prefix = ''
        return prefix + str(self.number).zfill(3)

    def get_type_verbose(self):
        if self.type == 'university':
            return 'Университет'
        elif self.type == 'hostel':
            return 'Общежитие'


class RequestLog(models.Model):
    class RequestStatus(models.TextChoices):
        CREATED = 'created', 'Создана'
        ACTIVATED = 'activated', 'Активирована'
        PROCESSING = 'processing', 'Обрабатывается'
        CANCELLED = 'cancelled', 'Отменена'
        CLOSED = 'closed', 'Закрыта'
        POSTPONED = 'postponed', 'Отложена'

    request = models.ForeignKey(Request, on_delete=models.RESTRICT)
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True, blank=True,
                                   verbose_name='Специалист')
    status = models.CharField(max_length=15, verbose_name='Статус', choices=RequestStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    class Meta:
        ordering = ['created_at']
        get_latest_by = 'created_at'
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'

    def __str__(self):
        return str(self.request.pk) + ' - ' + self.status + ' - ' + self.created_at.strftime('%d.%m.%Y %H:%M')

    def get_status_verbose(self):
        return self.RequestStatus.labels[self.RequestStatus.values.index(self.status)]


class Note(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   verbose_name='Специалист')
    text = models.CharField(max_length=200, verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    removed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата удаления')

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'
        verbose_name = 'Примечание'
        verbose_name_plural = 'Примечания'

    def __str__(self):
        return str(self.request_id) + ' - ' + str(self.specialist_id) + ' - ' + self.text
