from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileView, UserSearchView,
    FriendshipRequestViewSet, FriendsView, BlockView,
    PostViewSet, CommentViewSet, ReactionView,
    GroupViewSet, PageViewSet,
    ThreadViewSet, NotificationViewSet,
    AdminAuditLogView, AdminUsersView, AdminPostHideView,
)

router = DefaultRouter()
router.register(r'friends/requests', FriendshipRequestViewSet, basename='friend-request')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'pages', PageViewSet, basename='page')
router.register(r'threads', ThreadViewSet, basename='thread')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path(
        'threads/<uuid:thread_id>/messages/',
        ThreadViewSet.as_view({'get': 'thread_messages', 'post': 'thread_send_message'}),
    ),
    path('threads/<uuid:thread_id>/read/', ThreadViewSet.as_view({'post': 'thread_read'})),
    path('threads/<uuid:thread_id>/typing/', ThreadViewSet.as_view({'get': 'thread_typing'})),
    path('', include(router.urls)),
    path('me/', UserProfileView.as_view(), name='me'),
    path('users/<uuid:user_id>/', UserProfileView.as_view(), name='user-profile'),
    path('users/', UserSearchView.as_view(), name='user-search'),
    path('users/<uuid:user_id>/friends/', FriendsView.as_view(), name='user-friends'),
    path('users/<uuid:user_id>/posts/', PostViewSet.as_view({'get': 'user_posts'}), name='user-posts'),
    path('friends/<uuid:user_id>/', FriendsView.as_view(), name='friend-delete'),
    path('users/<uuid:user_id>/block/', BlockView.as_view(), name='block-user'),
    path('posts/<uuid:post_id>/comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='post-comments'),
    path('comments/<uuid:pk>/', CommentViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='comment-detail'),
    path('posts/<uuid:post_id>/reactions/', ReactionView.as_view(), name='post-reactions'),
    path('comments/<uuid:comment_id>/reactions/', ReactionView.as_view(), name='comment-reactions'),
    path('posts/<uuid:post_id>/report/', PostViewSet.as_view({'post': 'report'}), name='report-post'),
    path('search/posts/', PostViewSet.as_view({'get': 'search'}), name='search-posts'),
    path('posts/trending/', PostViewSet.as_view({'get': 'trending'}), name='trending-posts'),
    path('groups/<slug:slug>/posts/', GroupViewSet.as_view({'get': 'posts'}), name='group-posts'),
    path('admin/audit_logs/', AdminAuditLogView.as_view(), name='admin-audit'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/posts/<uuid:post_id>/hide/', AdminPostHideView.as_view(), name='admin-hide-post'),
]
