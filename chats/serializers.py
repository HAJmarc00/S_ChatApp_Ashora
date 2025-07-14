from rest_framework import serializers
from .models import Chat, ChatParticipant, Message, Block
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model
from groups.models import Group

User = get_user_model()

class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['user', 'is_muted', 'is_blocked', 'joined_at']


class ChatSerializer(serializers.ModelSerializer):
    chat_participants = ChatParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'chat_type', 'group', 'created_at', 'chat_participants']


class CreatePrivateChatSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
    group_id = serializers.IntegerField(required=False)

    def validate(self, data):
        chat_type = self.context['chat_type']
        request_user = self.context['request'].user

        if chat_type == 'private':
            if not data.get('user_id'):
                raise serializers.ValidationError({"user_id": "This field is required for private chats."})
            if data['user_id'] == request_user.id:
                raise serializers.ValidationError({"user_id": "You can't start a chat with yourself."})
            if not User.objects.filter(id=data['user_id']).exists():
                raise serializers.ValidationError({"user_id": "User not found."})
        elif chat_type == 'group':
            if not data.get('group_id'):
                raise serializers.ValidationError({"group_id": "This field is required for group chats."})
            if not Group.objects.filter(id=data['group_id']).exists():
                raise serializers.ValidationError({"group_id": "Group not found."})
        else:
            raise serializers.ValidationError({"chat_type": "Invalid chat type."})

        return data

    def create(self, validated_data):
        chat_type = self.context['chat_type']
        request_user = self.context['request'].user

        if chat_type == 'private':
            other_user = User.objects.get(id=validated_data['user_id'])
            chat = Chat.objects.filter(chat_type='private').filter(
                chat_participants__user=request_user
            ).filter(chat_participants__user=other_user).distinct().first()

            if chat:
                return chat

            chat = Chat.objects.create(chat_type='private')
            ChatParticipant.objects.create(chat=chat, user=request_user)
            ChatParticipant.objects.create(chat=chat, user=other_user)
            return chat

        elif chat_type == 'group':
            group = Group.objects.get(id=validated_data['group_id'])
            chat, created = Chat.objects.get_or_create(chat_type='group', group=group)
            ChatParticipant.objects.get_or_create(chat=chat, user=request_user)
            return chat


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'file', 'created_at', 'is_edited']


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'file']

    def validate(self, data):
        if not data.get('content') and not data.get('file'):
            raise serializers.ValidationError("Message must have either content or a file.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        chat = self.context['chat']
        return Message.objects.create(sender=user, chat=chat, **validated_data)


class BlockSerializer(serializers.ModelSerializer):
    blocker = UserSerializer(read_only=True)
    blocked = UserSerializer(read_only=True)

    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'created_at']
