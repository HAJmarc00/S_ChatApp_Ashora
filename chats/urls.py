from django.urls import path
from .views import (
    CreateChatView,
    ChatListView,
    ChatDetailView,
    SendMessageView,
    MessageListView,
    BlockUserView,
    UnblockUserView,
)

urlpatterns = [
    path('chat/create/', CreateChatView.as_view(), name='create_chat'),  # private or group
    path('', ChatListView.as_view(), name='chat_list'),
    path('<int:chat_id>/', ChatDetailView.as_view(), name='chat_detail'),
    path('<int:chat_id>/send/', SendMessageView.as_view(), name='send_message'),
    path('<int:chat_id>/messages/', MessageListView.as_view(), name='message_list'),
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('unblock/', UnblockUserView.as_view(), name='unblock_user'),
]
