from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Chat, ChatParticipant, Message, Block
from .serializers import (
    ChatSerializer,
    CreatePrivateChatSerializer,
    MessageSerializer,
    CreateMessageSerializer,
    BlockSerializer
)
from django.contrib.auth import get_user_model
from groups.models import Group
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(chat_participants__user=self.request.user).distinct()


class CreateChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        chat_type = request.data.get("chat_type")
        if chat_type not in ['private', 'group']:
            return Response({"detail": "chat_type must be 'private' or 'group'."}, status=400)

        if chat_type == 'private':
            user_id = request.data.get("user_id")
            if not user_id:
                return Response({"detail": "user_id is required for private chat."}, status=400)
            if int(user_id) == request.user.id:
                return Response({"detail": "You cannot chat with yourself."}, status=400)

            other_user = get_object_or_404(User, id=user_id)

            # Check if chat already exists
            existing_chat = Chat.objects.filter(
                chat_type='private',
                chat_participants__user=request.user
            ).filter(chat_participants__user=other_user).first()

            if existing_chat:
                return Response(ChatSerializer(existing_chat).data, status=200)

            chat = Chat.objects.create(chat_type='private')
            ChatParticipant.objects.create(chat=chat, user=request.user)
            ChatParticipant.objects.create(chat=chat, user=other_user)
            return Response(ChatSerializer(chat).data, status=201)

        elif chat_type == 'group':
            group_id = request.data.get("group_id")
            if not group_id:
                return Response({"detail": "group_id is required for group chat."}, status=400)

            group = get_object_or_404(Group, id=group_id)

            # Check if chat already exists
            if Chat.objects.filter(chat_type='group', group=group).exists():
                return Response({"detail": "Chat for this group already exists."}, status=400)

            chat = Chat.objects.create(chat_type='group', group=group)
            members = group.members.all()
            for member in members:
                ChatParticipant.objects.create(chat=chat, user=member.user)
            return Response(ChatSerializer(chat).data, status=201)
        

class ChatDetailView(generics.RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(chat_participants__user=self.request.user)


class SendMessageView(generics.CreateAPIView):
    serializer_class = CreateMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        if not ChatParticipant.objects.filter(chat=chat, user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not a participant in this chat.")
        serializer.save(chat=chat, sender=self.request.user)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        if not ChatParticipant.objects.filter(chat=chat, user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not a participant in this chat.")
        return Message.objects.filter(chat=chat).order_by('created_at')


class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        blocked_id = request.data.get('blocked_id')
        if not blocked_id:
            return Response({"detail": "blocked_id is required."}, status=400)

        if int(blocked_id) == request.user.id:
            return Response({"detail": "You cannot block yourself."}, status=400)

        blocked_user = get_object_or_404(User, id=blocked_id)

        block, created = Block.objects.get_or_create(
            blocker=request.user,
            blocked=blocked_user
        )

        if not created:
            return Response({"detail": "User is already blocked."}, status=200)

        return Response(BlockSerializer(block).data, status=201)


class UnblockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        blocked_id = request.data.get('blocked_id')
        if not blocked_id:
            return Response({"detail": "blocked_id is required."}, status=400)

        Block.objects.filter(blocker=request.user, blocked_id=blocked_id).delete()
        return Response({"detail": "User unblocked."}, status=200)
