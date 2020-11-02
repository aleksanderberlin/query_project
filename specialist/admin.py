from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import CustomSpecialistChangeForm, CustomSpecialistCreationForm
# Register your models here.


class CustomSpecialistAdmin(UserAdmin):
    add_form = CustomSpecialistCreationForm
    form = CustomSpecialistChangeForm
    model = Specialist
    list_display = UserAdmin.list_display + ('room', 'table_number',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('room', 'table_number',)}),
    )


admin.site.register(Specialist, CustomSpecialistAdmin)
