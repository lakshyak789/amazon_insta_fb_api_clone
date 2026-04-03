from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileView, UserSearchView,
    FollowView, FollowersView, FollowingView, FollowSuggestionsView, FollowRequestView,
    MediaViewSet, MediaCommentViewSet, CommentViewSet,
    StoryViewSet, TagViewSet, SearchView, PlaceViewSet,
    DMThreadViewSet, NotificationViewSet,
    AdminUserView, AdminUserVerifyView, AdminAuditLogView, AdminTrendsTagsView, AdminAbuseReportView
)

router = DefaultRouter()
router.register(r'media', MediaViewSet, basename='media')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'dm/threads', DMThreadViewSet, basename='dm-thread')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserProfileView.as_view(), name='me'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('users/', UserSearchView.as_view(), name='user-search'),
    path('users/<uuid:user_id>/follow/', FollowView.as_view(), name='follow-user'),
    path('users/<uuid:user_id>/followers/', FollowersView.as_view(), name='user-followers'),
    path('users/<uuid:user_id>/following/', FollowingView.as_view(), name='user-following'),
    path('users/<uuid:user_id>/media/', MediaViewSet.as_view({'get': 'user_media'}), name='user-media'),
    path('users/<uuid:user_id>/stories/', StoryViewSet.as_view({'get': 'user_stories'}), name='user-stories'),
    path('me/follow_suggestions/', FollowSuggestionsView.as_view(), name='follow-suggestions'),
    path('follow_requests/<uuid:request_id>/', FollowRequestView.as_view(), name='follow-request'),
    path('media/<uuid:pk>/comments/', MediaCommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='media-comments'),
    path('media/<uuid:pk>/archive/', MediaViewSet.as_view({'post': 'archive_toggle', 'delete': 'archive_toggle'}), name='media-archive'),
    path('media/<uuid:pk>/report/', MediaViewSet.as_view({'post': 'report'}), name='report-media'),
    path('comments/<uuid:pk>/report/', CommentViewSet.as_view({'post': 'report'}), name='report-comment'),
    path('search/', SearchView.as_view(), name='search'),
    path('places/', PlaceViewSet.as_view({'get': 'list'}), name='places'),
    path('dm/threads/<uuid:pk>/messages/', DMThreadViewSet.as_view({'get': 'messages'}), name='thread-messages'),
    path('dm/threads/<uuid:pk>/messages/send/', DMThreadViewSet.as_view({'post': 'send_message'}), name='send-message'),
    path('dm/threads/<uuid:pk>/read/', DMThreadViewSet.as_view({'post': 'read'}), name='thread-read'),
    path('dm/threads/<uuid:pk>/leave/', DMThreadViewSet.as_view({'post': 'leave'}), name='thread-leave'),
    path('feed/', MediaViewSet.as_view({'get': 'feed'}), name='feed'),
    path('explore/', MediaViewSet.as_view({'get': 'explore'}), name='explore'),
    path('mentions/', NotificationViewSet.as_view({'get': 'mentions'}), name='mentions'),
    path('admin/users/', AdminUserView.as_view(), name='admin-users'),
    path('admin/users/<uuid:user_id>/verify/', AdminUserVerifyView.as_view(), name='admin-verify-user'),
    path('admin/audit_logs/', AdminAuditLogView.as_view(), name='admin-audit'),
    path('admin/trends/tags/', AdminTrendsTagsView.as_view(), name='admin-trends'),
    path('admin/abuse/reports/', AdminAbuseReportView.as_view(), name='admin-abuse'),
    path('admin/abuse/reports/<str:pk>/resolve/', AdminAbuseReportView.as_view(), name='admin-resolve-abuse'),
]
