from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Specialist(AbstractUser):
    table_number = models.IntegerField(verbose_name='Номер стола', blank=True, null=True)