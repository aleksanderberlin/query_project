from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(User)
admin.site.register(Request)
admin.site.register(Specialist, UserAdmin)
admin.site.register(RequestLog)
admin.site.register(Permission)