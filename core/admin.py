from django.contrib import admin
from .models import SystemSettings, CeleryTaskLogs

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description', 'updated_by', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('updated_at',)
    
    # Save the admin user who modifies a configuration row automatically
    def save_model(self, request, obj, form, change):
        if change:  # Only update if editing an existing setting
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CeleryTaskLogs)
class CeleryTaskLogsAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'task_id', 'status', 'expense', 'executed_at', 'completed_at')
    list_filter = ('status', 'executed_at')
    search_fields = ('task_name', 'task_id', 'result')
    readonly_fields = ('task_name', 'task_id', 'status', 'expense', 'result', 'executed_at', 'completed_at')
    ordering = ('-executed_at',)

    # Prevent admins from manually tempering with or changing background worker logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
