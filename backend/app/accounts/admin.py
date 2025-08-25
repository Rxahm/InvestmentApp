from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Account

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'two_factor_secret')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'description')
    search_fields = ('code', 'name', 'type')
    list_filter = ('type',)

# Register your models here
admin.site.register(User, CustomUserAdmin)
