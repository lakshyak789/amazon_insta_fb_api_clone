from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from core.pagination import StandardResultsSetPagination
from core.models import User
from .models import Follow, Media, Story, Comment, Like, Tag, MediaTag, DirectThread, DirectParticipant, DirectMessage, Notification
from .serializers import (
    MediaSerializer, MediaListSerializer, CommentSerializer,
    FollowSerializer, LikeSerializer, TagSerializer, StorySerializer,
    DirectThreadSerializer, DirectMessageSerializer, NotificationSerializer
)


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username=None):
        if username:
            user = get_object_or_404(User, username=username)
        else:
            user = request.user
        return Response({
            'id': str(user.id),
            'username': getattr(user, 'username', ''),
            'fullName': getattr(user, 'full_name', ''),
            'bio': getattr(user, 'bio', ''),
            'avatarUrl': getattr(user, 'avatar_url', None),
            'isVerified': getattr(user, 'is_verified', False),
            'followers': Follow.objects.filter(followee=user, status='accepted').count(),
            'following': Follow.objects.filter(follower=user, status='accepted').count()
        })


class UserSearchView(APIView):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        q = request.query_params.get('q', '')
        users = User.objects.filter(username__icontains=q)[:20]
        return Response([{
            'id': str(u.id),
            'username': getattr(u, 'username', ''),
            'avatarUrl': getattr(u, 'avatar_url', None)
        } for u in users])


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        followee = get_object_or_404(User, id=user_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            followee=followee,
            defaults={'status': 'accepted'}
        )
        if not created:
            if follow.status == 'blocked':
                return Response({'error': {'code': 'BLOCKED'}}, status=400)
            follow.status = 'accepted'
            follow.save()
        Notification.objects.create(user=followee, type='follow', ref_type='user', ref_id=request.user.id)
        return Response({'status': follow.status})

    def delete(self, request, user_id):
        Follow.objects.filter(follower=request.user, followee_id=user_id).delete()
        return Response(status=204)


class FollowersView(APIView):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id) if user_id else request.user
        followers = Follow.objects.filter(followee=user, status='accepted')
        return Response([{
            'id': str(f.follower.id),
            'username': getattr(f.follower, 'username', '')
        } for f in followers])


class FollowingView(APIView):
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id) if user_id else request.user
        following = Follow.objects.filter(follower=user, status='accepted')
        return Response([{
            'id': str(f.followee.id),
            'username': getattr(f.followee, 'username', '')
        } for f in following])


class FollowSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        following_ids = Follow.objects.filter(follower=request.user).values_list('followee_id', flat=True)
        suggestions = User.objects.exclude(id__in=list(following_ids) + [request.user.id])[:10]
        return Response([{
            'id': str(u.id),
            'username': getattr(u, 'username', '')
        } for u in suggestions])


class FollowRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        action_type = request.data.get('action')
        follow = get_object_or_404(Follow, id=request_id)
        if action_type == 'approve':
            follow.status = 'accepted'
            follow.save()
        elif action_type == 'decline':
            follow.delete()
        return Response(status=204)


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ('retrieve', 'explore', 'likes', 'user_media'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            if self.action == 'user_media':
                user_id = self.kwargs.get('user_id')
                return Media.objects.filter(owner_id=user_id, is_archived=False)
            if self.action == 'explore':
                return Media.objects.annotate(score=Count('like_count') + Count('comment_count')).order_by('-score')[:50]
            if self.action in ('retrieve', 'likes'):
                return Media.objects.all()
            return Media.objects.none()

        if self.action == 'feed':
            following_ids = Follow.objects.filter(follower=user, status='accepted').values_list('followee_id', flat=True)
            return Media.objects.filter(owner_id__in=list(following_ids) + [user.id], is_archived=False)
        elif self.action == 'explore':
            return Media.objects.annotate(score=Count('like_count') + Count('comment_count')).order_by('-score')[:50]
        elif self.action == 'user_media':
            user_id = self.kwargs.get('user_id')
            return Media.objects.filter(owner_id=user_id, is_archived=False)
        elif self.action in ['archive_toggle', 'archive_media']:
            return Media.objects.filter(owner=user)
        return Media.objects.filter(owner=user, is_archived=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaListSerializer
        return MediaSerializer

    def create(self, request):
        urls = request.data.get('urls', {'items': [{'url': request.data.get('url', ''), 'width': 1080, 'height': 1080}]})
        media = Media.objects.create(
            owner=request.user,
            type=request.data.get('type', 'image'),
            urls=urls,
            caption=request.data.get('caption', ''),
            location=request.data.get('location', '')
        )
        tags = request.data.get('tags', [])
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            tag.usage_count += 1
            tag.save()
            MediaTag.objects.create(media=media, tag=tag)
        return Response(MediaSerializer(media).data, status=201)

    def partial_update(self, request, *args, **kwargs):
        media = self.get_object()
        if media.owner != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        media = self.get_object()
        if media.owner != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        media.delete()
        return Response(status=204)

    @action(detail=True, methods=['post', 'delete'], url_path='archive')
    def archive_toggle(self, request, pk=None):
        media = self.get_object()
        if request.method == 'POST':
            media.is_archived = True
            media.save()
        else:
            media.is_archived = False
            media.save()
        return Response(MediaSerializer(media).data)

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        media = self.get_object()
        if request.method == 'POST':
            like, created = Like.objects.get_or_create(user=request.user, media=media)
            if created:
                media.like_count += 1
                media.save()
                Notification.objects.create(user=media.owner, type='like', ref_type='media', ref_id=media.id)
            return Response({'likes': media.like_count, 'liked': created})
        else:
            Like.objects.filter(user=request.user, media=media).delete()
            media.like_count = max(0, media.like_count - 1)
            media.save()
            return Response({'likes': media.like_count, 'liked': False})

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        media = self.get_object()
        likes = Like.objects.filter(media=media)
        return Response([{'user_id': str(l.user.id)} for l in likes])

    @action(detail=False, methods=['get'])
    def feed(self, request):
        media = self.get_queryset()
        page = self.paginate_queryset(media)
        if page is not None:
            return self.get_paginated_response(MediaSerializer(page, many=True).data)
        return Response(MediaSerializer(media, many=True).data)

    @action(detail=False, methods=['get'])
    def explore(self, request):
        media = self.get_queryset()
        return Response(MediaSerializer(media, many=True).data)

    @action(detail=False, methods=['get'], url_path='user_media')
    def user_media(self, request, user_id=None):
        media = Media.objects.filter(owner_id=user_id, is_archived=False)
        return Response(MediaSerializer(media, many=True).data)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        return Response({'ok': True})


class MediaCommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        media_id = self.kwargs.get('media_id') or self.kwargs.get('pk')
        return Comment.objects.filter(media_id=media_id)

    def create(self, request, pk=None, media_id=None, **kwargs):
        media_id = media_id or pk or kwargs.get('pk')
        media = get_object_or_404(Media, id=media_id)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, media=media)
        media.comment_count += 1
        media.save()
        Notification.objects.create(user=media.owner, type='comment', ref_type='media', ref_id=media.id)
        return Response(serializer.data, status=201)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        comment.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        return Response({'ok': True})


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'user_stories':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'combined':
            following_ids = Follow.objects.filter(follower=self.request.user, status='accepted').values_list('followee_id', flat=True)
            return Story.objects.filter(owner_id__in=list(following_ids) + [self.request.user.id], expires_at__gt=timezone.now())
        elif self.action == 'user_stories':
            user_id = self.kwargs.get('user_id')
            return Story.objects.filter(owner_id=user_id, expires_at__gt=timezone.now())
        return Story.objects.filter(owner=self.request.user)

    def create(self, request):
        expires_in = request.data.get('expiresIn', 86400)
        if isinstance(expires_in, str):
            expires_in = int(expires_in)
        story = Story.objects.create(
            owner=request.user,
            media_url=request.data.get('url', ''),
            expires_at=timezone.now() + timedelta(seconds=expires_in)
        )
        return Response(StorySerializer(story).data, status=201)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        story = self.get_object()
        story.view_count += 1
        story.save()
        return Response({'viewCount': story.view_count})

    @action(detail=False, methods=['get'])
    def combined(self, request):
        stories = self.get_queryset()
        return Response(StorySerializer(stories, many=True).data)

    @action(detail=False, methods=['get'], url_path='user_stories')
    def user_stories(self, request, user_id=None):
        stories = self.get_queryset()
        return Response(StorySerializer(stories, many=True).data)

    @action(detail=True, methods=['get'])
    def viewers(self, request, pk=None):
        story = self.get_object()
        return Response([])

    def destroy(self, request, *args, **kwargs):
        story = self.get_object()
        if story.owner != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        story.delete()
        return Response(status=204)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ('list', 'media'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        q = self.request.query_params.get('q', '')
        return Tag.objects.filter(name__icontains=q).order_by('-usage_count')

    @action(detail=True, methods=['get'])
    def media(self, request, pk=None):
        tag = self.get_object()
        media_tags = MediaTag.objects.filter(tag=tag)
        media_ids = [mt.media_id for mt in media_tags]
        media = Media.objects.filter(id__in=media_ids)
        return Response(MediaSerializer(media, many=True).data)


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '')
        type_filter = request.query_params.get('type', 'user')

        if type_filter == 'user' or type_filter is None:
            users = User.objects.filter(username__icontains=q)[:20]
            return Response([{'type': 'user', 'id': str(u.id), 'username': getattr(u, 'username', '')} for u in users])
        elif type_filter == 'tag':
            tags = Tag.objects.filter(name__icontains=q)[:20]
            return Response([{'type': 'tag', 'id': str(t.id), 'name': t.name} for t in tags])
        elif type_filter == 'place':
            return Response([])
        return Response([])


class PlaceViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        q = self.request.query_params.get('q', '')
        return (
            Media.objects.filter(location__icontains=q)
            .order_by('location', '-id')
            .distinct('location')[:50]
        )


class DMThreadViewSet(viewsets.ModelViewSet):
    serializer_class = DirectThreadSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        threads = DirectParticipant.objects.filter(user=self.request.user).values_list('thread_id', flat=True)
        return DirectThread.objects.filter(id__in=threads)

    def create(self, request):
        participant_ids = request.data.get('participantIds', [])
        if isinstance(participant_ids, str):
            participant_ids = [participant_ids]
        user_ids = [uid for uid in participant_ids] + [str(request.user.id)]
        thread = DirectThread.objects.create(is_group=len(user_ids) > 2)
        for uid in user_ids:
            DirectParticipant.objects.create(thread=thread, user_id=uid)
        return Response(DirectThreadSerializer(thread).data, status=201)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        thread = self.get_object()
        messages = thread.ig_messages.all()
        return Response(DirectMessageSerializer(messages, many=True).data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        thread = self.get_object()
        message = DirectMessage.objects.create(
            thread=thread,
            sender=request.user,
            body=request.data.get('body', ''),
            media_url=request.data.get('media', '')
        )
        return Response(DirectMessageSerializer(message).data, status=201)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def typing(self, request, pk=None):
        return Response({'typing': False})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        DirectParticipant.objects.filter(thread_id=pk, user=request.user).delete()
        return Response(status=204)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(status=204)

    @action(detail=False, methods=['get'])
    def mentions(self, request):
        mentions = Notification.objects.filter(user=request.user, type='mention')
        return Response(NotificationSerializer(mentions, many=True).data)


class AdminUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()[:50]
        return Response([{
            'id': str(u.id),
            'username': getattr(u, 'username', ''),
            'isVerified': getattr(u, 'is_verified', False)
        } for u in users])


class AdminUserVerifyView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_verified = request.data.get('is_verified', False)
        user.save()
        return Response({'id': str(user.id), 'isVerified': user.is_verified})


class AdminAuditLogView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response([])


class AdminTrendsTagsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        limit = int(request.query_params.get('limit', 10))
        tags = Tag.objects.order_by('-usage_count')[:limit]
        return Response([{'name': t.name, 'usage_count': t.usage_count} for t in tags])


class AdminAbuseReportView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        return Response([])

    def post(self, request, pk=None):
        return Response({'status': 'resolved'})
