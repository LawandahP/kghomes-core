from django.contrib import admin
from .models import Property, Kind, Type, Amenities
# Register your models here.





class PropertyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "address", "owner", "property_kind", "property_type"]
    list_filter = ('owner',)
    
    ordering = ["id"]
    # fieldsets = (
    #     ('Login', {'fields': ('email', 'phone_number', 'username', 'password' )}),
    #     ('Personal info', {'fields': ('full_name',)}),
    #     ('Account info', {'fields': ('account',)}),
    #     ('Permissions', {'fields': ('is_active','is_staff', 'is_superuser', 'groups', 'user_permissions',)}),
    # )
    # add_fieldsets = (
    #     ('User Details', {
    #         'classes': ('wide',),
    #         'fields': ('full_name', 'email', 'phone_number', 'password1', 'password2'),
    #     }),
    #     ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions',)})
    # )

admin.site.register(Property, PropertyAdmin)
admin.site.register(Kind)
admin.site.register(Type)
admin.site.register(Amenities)
