from django.contrib import admin
from .models import Group, GroupMember, GroupInvite


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_public', 'created_at')
    readonly_fields = ('created_at', 'avatar_preview')
    fields = (
        'name', 'description', 'avatar', 'avatar_preview',
        'is_public', 'owner', 'pinned_message', 'created_at'
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="height: 50px;"/>'
        return "-"
    avatar_preview.allow_tags = True
    avatar_preview.short_description = 'Avatar Preview'


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_admin', 'is_approved', 'joined_at')
    list_filter = ('is_admin', 'is_approved', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)
    list_editable = ('is_admin', 'is_approved')


@admin.register(GroupInvite)
class GroupInviteAdmin(admin.ModelAdmin):
    list_display = ('group', 'inviter', 'code', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('group__name', 'inviter__username', 'code')
    readonly_fields = ('created_at',)
