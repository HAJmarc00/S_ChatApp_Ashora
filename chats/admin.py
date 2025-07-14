from django.contrib import admin
from .models import Chat, ChatParticipant, Message, MessageStatus, Block

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_type', 'get_group_name', 'created_at')
    list_filter = ('chat_type', 'created_at')
    search_fields = ('chat_type', 'group__name')

    def get_group_name(self, obj):
        return obj.group.name if obj.group else "-"
    get_group_name.short_description = 'Group Name'


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'is_muted', 'is_blocked', 'joined_at')
    list_filter = ('is_muted', 'is_blocked', 'joined_at')
    search_fields = ('user__username', 'chat__id')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'short_content', 'created_at', 'is_edited')
    list_filter = ('created_at', 'is_edited')
    search_fields = ('sender__username', 'content')

    def short_content(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'


@admin.register(MessageStatus)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'user', 'is_read', 'read_at')
    list_filter = ('is_read', 'read_at')
    search_fields = ('user__username',)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked__username')
