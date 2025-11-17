"""
Accounts App Admin Configuration
Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
"""
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model
    Reference: https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    """
    list_display = ['get_username', 'follower_count', 'following_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at', 'updated_at', 'get_blog_count']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile_image')
        }),
        ('Bio', {
            'fields': ('bio',)
        }),
        ('Statistics', {
            'fields': ('follower_count', 'following_count', 'get_blog_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_username(self, obj):
        """Display username in list view"""
        return obj.user.username
    get_username.short_description = 'Username'

