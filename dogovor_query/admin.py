from django.contrib import admin
from .models import *
from django.contrib.auth.models import Permission
from django.contrib.admin import SimpleListFilter


class IsRemovedFilter(SimpleListFilter):
    title = 'Удалено?'
    parameter_name = 'is_removed'

    def lookups(self, request, model_admin):
        return [('False', 'Да'), ('True', 'Нет')]

    def queryset(self, request, queryset):
        if self.value() == 'False':
            return queryset.filter(removed_at__isnull=False)
        elif self.value() == 'True':
            return queryset.filter(removed_at__isnull=True)
        else:
            return queryset.all()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'last_name', 'first_name', 'second_name', 'birthday', 'phone_number')
    ordering = ['-created_at',]
    list_filter = (IsRemovedFilter, )


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user_id', 'number', 'type', 'question')
    ordering = ['-created_at']
    list_filter = ('type', 'created_at', IsRemovedFilter)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'specialist_id', 'status')
    ordering = ['-created_at']
    list_filter = ('specialist', 'status', 'created_at', IsRemovedFilter)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'specialist_id', 'text')
    ordering = ['-created_at']
    list_filter = ('specialist', 'created_at', IsRemovedFilter)


admin.site.register(Permission)
