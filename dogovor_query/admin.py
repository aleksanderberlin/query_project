from django.contrib import admin
from .models import *
from .forms import CustomSpecialistChangeForm, CustomSpecialistCreationForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin


class CustomSpecialistAdmin(UserAdmin):
    add_form = CustomSpecialistCreationForm
    form = CustomSpecialistChangeForm
    model = Specialist
    list_display = ['username', 'email', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('table_number',)}),
    )


# Register your models here.
admin.site.register(User)
admin.site.register(Request)
admin.site.register(Specialist, CustomSpecialistAdmin)
admin.site.register(RequestLog)
admin.site.register(Permission)
