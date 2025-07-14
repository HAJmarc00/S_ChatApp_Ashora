from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from accounts.serializers import UserSerializer
from .models import Group, GroupMember, GroupInvite
from .serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    GroupMemberSerializer,
    GroupMemberManageSerializer,
    GroupInviteSerializer,
)
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        GroupMember.objects.create(group=group, user=self.request.user, is_admin=True)


class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members__user=self.request.user) | Group.objects.filter(is_public=True)


class GroupDetailView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupUpdateView(generics.UpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        group = self.get_object()
        if self.request.user != group.owner:
            raise permissions.PermissionDenied("Only the group owner can update the group.")
        serializer.save()


class GroupDeleteView(generics.DestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user != instance.owner:
            raise permissions.PermissionDenied("Only the group owner can delete the group.")
        instance.delete()


class JoinGroupView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not group.is_public:
            return Response({"detail": "Private group. Invite required."}, status=403)
        GroupMember.objects.get_or_create(group=group, user=request.user)
        return Response({"detail": "Joined group."})


class LeaveGroupView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        GroupMember.objects.filter(group=group, user=request.user).delete()
        return Response({"detail": "Left group."})


class AddMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can add members."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        GroupMember.objects.get_or_create(group=group, user=user)
        return Response({"detail": f"{user.username} added to group."})


class RemoveMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can remove members."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        GroupMember.objects.filter(group=group, user=user).delete()
        return Response({"detail": f"{user.username} removed from group."})


class PromoteMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can promote."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        member = get_object_or_404(GroupMember, group=group, user=user)
        member.is_admin = True
        member.save()
        return Response({"detail": f"{user.username} promoted to admin."})


class DemoteMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can demote."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        member = get_object_or_404(GroupMember, group=group, user=user)
        member.is_admin = False
        member.save()
        return Response({"detail": f"{user.username} demoted from admin."})


class ApproveMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id, user_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can approve members."}, status=403)

        member = get_object_or_404(GroupMember, group=group, user_id=user_id)
        member.is_approved = True
        member.save()
        return Response({"detail": "Member approved."})


class KickMemberView(generics.GenericAPIView):
    serializer_class = GroupMemberManageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id, user_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can kick members."}, status=403)

        GroupMember.objects.filter(group=group, user_id=user_id).delete()
        return Response({"detail": "Member removed."})


class CreateGroupInviteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can create invites."}, status=403)

        code = get_random_string(length=20)
        invite = GroupInvite.objects.create(group=group, code=code, created_by=request.user)
        serializer = GroupInviteSerializer(invite)
        return Response(serializer.data)


class UseGroupInviteView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, code):
        invite = get_object_or_404(GroupInvite, code=code, is_used=False)
        GroupMember.objects.get_or_create(group=invite.group, user=request.user)
        invite.is_used = True
        invite.save()
        return Response({"detail": "Joined group using invite."})


class PinMessageView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({"detail": "Only admins can pin messages."}, status=403)

        message = request.data.get("message")
        if not message:
            return Response({"detail": "No message provided."}, status=400)

        group.pinned_message = message
        group.save()
        return Response({"detail": "Message pinned."})
    
    
class GroupMemberListView(generics.ListAPIView):
    serializer_class = GroupMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        group = get_object_or_404(Group, id=group_id)

        # فقط اگر عضو گروه باشه، می‌تونه لیست اعضا رو ببینه
        if not GroupMember.objects.filter(group=group, user=self.request.user).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not a member of this group.")

        return GroupMember.objects.filter(group=group)
