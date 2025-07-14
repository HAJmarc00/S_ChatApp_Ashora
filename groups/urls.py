# groups/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Group CRUD
    path('create/', views.GroupCreateView.as_view(), name='group-create'),
    path('', views.GroupListView.as_view(), name='group-list'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/update/', views.GroupUpdateView.as_view(), name='group-update'),
    path('<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group-delete'),
    path('<int:group_id>/members/', views.GroupMemberListView.as_view(), name='group_members'),

    # Joining / Leaving Groups
    path('<int:group_id>/join/', views.JoinGroupView.as_view(), name='group-join'),
    path('<int:group_id>/leave/', views.LeaveGroupView.as_view(), name='group-leave'),

    # Member Management
    path('<int:group_id>/members/add/', views.AddMemberView.as_view(), name='group-member-add'),
    path('<int:group_id>/members/remove/', views.RemoveMemberView.as_view(), name='group-member-remove'),
    path('<int:group_id>/members/promote/', views.PromoteMemberView.as_view(), name='group-member-promote'),
    path('<int:group_id>/members/demote/', views.DemoteMemberView.as_view(), name='group-member-demote'),
    path('<int:group_id>/members/<int:user_id>/approve/', views.ApproveMemberView.as_view(), name='group-member-approve'),
    path('<int:group_id>/members/<int:user_id>/kick/', views.KickMemberView.as_view(), name='group-member-kick'),

    # Invites
    path('<int:group_id>/invites/create/', views.CreateGroupInviteView.as_view(), name='group-invite-create'),
    path('invites/use/<str:code>/', views.UseGroupInviteView.as_view(), name='group-invite-use'),

    # Pinning Messages
    path('<int:group_id>/pin/', views.PinMessageView.as_view(), name='group-pin-message'),
]
    