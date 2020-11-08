from django.db import models
from django.contrib.auth.models import AbstractUser


class Specialist(AbstractUser):
    ROOMS = [
        ('214 / 2', '214 / 2'),
        ('218 / 2', '218 / 2'),
    ]

    room = models.CharField(max_length=10, choices=ROOMS, verbose_name='Кабинет', null=True)
    table_number = models.IntegerField(verbose_name='Номер стола', null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['room', 'table_number'], name='unique_room_table'),
        ]
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def get_full_name(self):
        return self.last_name + ' ' + self.first_name

    def get_short_name(self):
        return self.last_name + ' ' + self.first_name[0] + '.'
