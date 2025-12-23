# accounts/admin.py
from django.contrib import admin
from .models import User, RecyclerProfile

class RecyclerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'status', 'rejection_count')
    list_filter = ('status',)
    actions = ['approve_recyclers', 'reject_recyclers']

    def approve_recyclers(self, request, queryset):
        # Update profile status
        queryset.update(status='APPROVED')
        # Update user permissions
        for profile in queryset:
            profile.user.is_recycler = True
            profile.user.save()
    approve_recyclers.short_description = "Approve selected recyclers"

    def reject_recyclers(self, request, queryset):
        for profile in queryset:
            profile.status = 'REJECTED'
            profile.rejection_count += 1
            profile.user.is_recycler = False # Ensure permission is revoked
            profile.user.save()
            profile.save()
    reject_recyclers.short_description = "Reject selected recyclers (Increases Strike Count)"

admin.site.register(User)
admin.site.register(RecyclerProfile, RecyclerProfileAdmin)