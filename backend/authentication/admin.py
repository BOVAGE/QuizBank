from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'bio', 'is_verified', 'is_staff']
    list_filter = ['is_verified', 'is_staff', 'is_superuser']


admin.site.unregister(Group)