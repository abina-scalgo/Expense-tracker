from rest_framework import serializers
from .models import SystemSettings

class SystemSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemSettings
        fields = ['id', 'key', 'value']
        read_only_fields = ['id', 'key']