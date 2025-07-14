from rest_framework import serializers
from .models import *
from accounts.serializers import UserSerializer  # فرض بر اینه که داری
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'avatar', 'is_public', 'owner', 'created_at', 'members_count']

    def get_members_count(self, obj):
        return obj.members.count()


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'description', 'avatar', 'is_public']


class GroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name', 'description', 'avatar', 'is_public']


class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'is_admin', 'joined_at']


class AddGroupMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("کاربر پیدا نشد.")
        return value

class GroupMemberManageSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("کاربر پیدا نشد.")
        return value

    def get_user(self):
        return User.objects.get(id=self.validated_data['user_id'])


class GroupInviteSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)  # یا می‌تونی GroupSerializer استفاده کنی

    class Meta:
        model = GroupInvite
        fields = ['id', 'group', 'code', 'is_used', 'created_at']
        read_only_fields = ['id', 'code', 'created_at']