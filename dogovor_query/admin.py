from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission

# Register your models here.
admin.site.register(User)
admin.site.register(Request)
admin.site.register(RequestLog)
admin.site.register(Permission)
admin.site.register(Note)
