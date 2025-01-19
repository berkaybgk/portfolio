from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'user', 'message', 'response', 'timestamp']
        read_only_fields = ['id', 'timestamp']
