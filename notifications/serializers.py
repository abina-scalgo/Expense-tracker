from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    #Maps directly to the target user_id
    user_id = serializers.PrimaryKeyRelatedField(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
