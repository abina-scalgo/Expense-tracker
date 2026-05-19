from django.contrib import admin
from .models import Notification, FcmTokens

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'fcm_sent', 'created_at')
    list_filter = ('is_read', 'type', 'fcm_sent', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at', 'fcm_sent_at')
    ordering = ('-created_at',)


@admin.register(FcmTokens)
class FcmTokensAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'device_type', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)
