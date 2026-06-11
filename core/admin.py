from django.contrib import admin
from .models import OrganizationInfo, ContactMessage

@admin.register(OrganizationInfo)
class OrganizationInfoAdmin(admin.ModelAdmin):
    # Update this list to display the translated fields in the admin dashboard panel list
    list_display = ('name_en', 'name_ne')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('name', 'email', 'subject')