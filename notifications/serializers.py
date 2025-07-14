from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer  # فرض بر اینه که اینو داری

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'actor', 'verb', 'target', 'timestamp', 'is_read']
        read_only_fields = ['recipient', 'timestamp']
