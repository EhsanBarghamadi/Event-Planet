from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    list_display = ('first_name', 'last_name', 'phone', 'is_staff', 'is_active')
    ordering = ('-created_at',)
    search_fields = ('phone', 'first_name', 'last_name')
    search_help_text = 'جست وجو بر اساس نام ، نام خانوادگی و شماره'
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    list_editable = ('is_active',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
