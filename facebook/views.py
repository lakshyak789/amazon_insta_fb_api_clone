import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.db.models import Q
from django.shortcuts import get_object_or_404

from core.pagination import StandardResultsSetPagination
from core.models import User
from .models import Friendship, Post, Comment, Reaction, Group, GroupMember, Page, Message, Notification
from .serializers import (
    FriendshipSerializer, PostSerializer, CommentSerializer,
    ReactionSerializer, GroupSerializer, GroupMemberSerializer,
    PageSerializer, MessageSerializer, NotificationSerializer
)


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        return Response({
            'id': str(user.id),
            'email': user.email,
            'fullName': user.full_name if hasattr(user, 'full_name') else user.email.split('@')[0],
            'username': user.username if hasattr(user, 'username') else '',
            'bio': user.bio if hasattr(user, 'bio') else '',
            'avatarUrl': user.avatar_url if hasattr(user, 'avatar_url') else None,
            'isActive': user.is_active
        })


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        q = request.query_params.get('q', '')
        users = User.objects.filter(
            Q(email__icontains=q) | Q(full_name__icontains=q)
        )[:20]
        return Response([{
            'id': str(u.id),
            'email': u.email,
            'fullName': u.full_name if hasattr(u, 'full_name') else u.email.split('@')[0]
        } for u in users])


class FriendshipRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FriendshipSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            incoming = self.request.query_params.get('type') != 'outgoing'
            if incoming:
                return Friendship.objects.filter(addressee=user, status='pending')
            return Friendship.objects.filter(requester=user, status='pending')
        return Friendship.objects.filter(Q(requester=user) | Q(addressee=user))

    def create(self, request):
        to_user_id = request.data.get('toUserId')
        addressee = get_object_or_404(User, id=to_user_id)
        friendship = Friendship.objects.create(requester=request.user, addressee=addressee)
        Notification.objects.create(user=addressee, type='friend_request', ref_type='friendship', ref_id=friendship.id)
        return Response(FriendshipSerializer(friendship).data, status=201)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        friendship = self.get_object()
        friendship.status = 'accepted'
        friendship.save()
        Notification.objects.create(user=friendship.requester, type='friend_request', ref_type='friendship', ref_id=friendship.id)
        return Response(FriendshipSerializer(friendship).data)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        friendship = self.get_object()
        friendship.status = 'declined'
        friendship.save()
        return Response(status=204)


class FriendsView(APIView):
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id) if user_id else request.user
        friendships = Friendship.objects.filter(
            (Q(requester=user) | Q(addressee=user)),
            status='accepted'
        )
        friend_ids = []
        for f in friendships:
            friend_ids.append(str(f.requester.id if f.requester != user else f.addressee.id))
        friends = User.objects.filter(id__in=friend_ids)[:20]
        return Response([{
            'id': str(u.id),
            'fullName': u.full_name if hasattr(u, 'full_name') else u.email.split('@')[0]
        } for u in friends])

    def delete(self, request, user_id=None):
        friendship = Friendship.objects.filter(
            Q(requester=request.user, addressee_id=user_id) |
            Q(requester_id=user_id, addressee=request.user)
        ).first()
        if friendship:
            friendship.delete()
        return Response(status=204)


class BlockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id=None):
        user = get_object_or_404(User, id=user_id)
        friendship, _ = Friendship.objects.get_or_create(requester=request.user, addressee=user)
        friendship.status = 'blocked'
        friendship.save()
        return Response({'blocked': True})

    def delete(self, request, user_id=None):
        friendship = Friendship.objects.filter(requester=request.user, addressee_id=user_id).first()
        if friendship:
            friendship.delete()
        return Response(status=204)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ('retrieve', 'trending', 'user_posts'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        auth = user.is_authenticated

        if self.action == 'feed':
            if not auth:
                return Post.objects.none()
            friendships = Friendship.objects.filter(
                Q(requester=user) | Q(addressee=user),
                status='accepted'
            )
            friend_ids = [f.addressee.id for f in friendships] + [f.requester.id for f in friendships] + [user.id]
            return Post.objects.filter(author_id__in=friend_ids).order_by('-created_at')

        if self.action == 'trending':
            return Post.objects.filter(privacy='public').order_by('-like_count', '-comment_count')[:20]

        if self.action == 'search':
            q = self.request.query_params.get('q', '')
            qs = Post.objects.filter(body__icontains=q)
            if not auth:
                qs = qs.filter(privacy='public')
            return qs.order_by('-created_at')

        if self.action == 'user_posts':
            user_id = self.kwargs.get('user_id')
            qs = Post.objects.filter(author_id=user_id)
            if not auth:
                qs = qs.filter(privacy='public')
            return qs.order_by('-created_at')

        if self.action == 'retrieve':
            if not auth:
                return Post.objects.filter(privacy='public')
            return Post.objects.all()

        if not auth:
            return Post.objects.none()

        if self.action in ('partial_update', 'destroy'):
            return Post.objects.filter(author=user)

        return Post.objects.filter(author=user).order_by('-created_at')

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=201)

    def partial_update(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user and not request.user.is_staff:
            return Response({'error': {'code': 'FORBIDDEN'}}, status=403)
        post.delete()
        return Response(status=204)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        if page is not None:
            return self.get_paginated_response(PostSerializer(page, many=True).data)
        return Response(PostSerializer(posts, many=True).data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        posts = self.get_queryset()
        return Response(PostSerializer(posts, many=True).data)

    def search(self, request):
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        if page is not None:
            return self.get_paginated_response(PostSerializer(page, many=True).data)
        return Response(PostSerializer(posts, many=True).data)

    def user_posts(self, request, user_id=None):
        posts = self.get_queryset()
        page = self.paginate_queryset(posts)
        if page is not None:
            return self.get_paginated_response(PostSerializer(page, many=True).data)
        return Response(PostSerializer(posts, many=True).data)

    @action(detail=True, methods=['get'])
    def shares(self, request, pk=None):
        post = self.get_object()
        return Response([])

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        return Response({'shared': True})

    @action(detail=True, methods=['get'])
    def visibility(self, request, pk=None):
        post = self.get_object()
        can_view = post.privacy == 'public' or (
            post.privacy == 'friends' and
            Friendship.objects.filter(Q(requester=request.user, addressee=post.author) | Q(requester=post.author, addressee=request.user), status='accepted').exists()
        )
        return Response({'privacy': post.privacy, 'canView': can_view})

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        return Response({'ok': True})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.filter(author=self.request.user)

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, post=post)
        post.comment_count += 1
        post.save()
        return Response(serializer.data, status=201)


class ReactionView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request, target_type=None, target_id=None, post_id=None, comment_id=None):
        if post_id:
            target_type = 'post'
            target_id = post_id
        elif comment_id:
            target_type = 'comment'
            target_id = comment_id
        
        reaction_type = request.data.get('type', 'like')

        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            target_type=target_type,
            target_id=target_id,
            defaults={'type': reaction_type}
        )
        if not created:
            reaction.type = reaction_type
            reaction.save()

        if target_type == 'post':
            post = get_object_or_404(Post, id=target_id)
            post.like_count = Reaction.objects.filter(target_type='post', target_id=target_id).count()
            post.save()

        return Response({'ok': True, 'type': reaction_type})

    def delete(self, request, target_type=None, target_id=None, post_id=None, comment_id=None):
        if post_id:
            target_type = 'post'
            target_id = post_id
        elif comment_id:
            target_type = 'comment'
            target_id = comment_id
            
        Reaction.objects.filter(user=request.user, target_type=target_type, target_id=target_id).delete()
        if target_type == 'post':
            post = get_object_or_404(Post, id=target_id)
            post.like_count = max(0, post.like_count - 1)
            post.save()
        return Response(status=204)

    def get(self, request, target_type=None, target_id=None, post_id=None, comment_id=None):
        if post_id:
            target_type = 'post'
            target_id = post_id
        elif comment_id:
            target_type = 'comment'
            target_id = comment_id
            
        reactions = Reaction.objects.filter(target_type=target_type, target_id=target_id)
        return Response([{'type': r.type, 'user_id': str(r.user.id)} for r in reactions])


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'posts'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'search':
            q = self.request.query_params.get('q', '')
            return Group.objects.filter(name__icontains=q)
        return Group.objects.all()

    def create(self, request):
        serializer = GroupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        GroupMember.objects.create(group=serializer.instance, user=request.user, role='admin')
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'])
    def join(self, request, slug=None):
        group = self.get_object()
        membership, created = GroupMember.objects.get_or_create(group=group, user=request.user)
        if not created:
            membership.status = 'joined'
            membership.save()
        return Response({'status': membership.status})

    @action(detail=True, methods=['post'])
    def leave(self, request, slug=None):
        GroupMember.objects.filter(group__slug=slug, user=request.user).delete()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def members(self, request, slug=None):
        group = self.get_object()
        user_id = request.data.get('userId')
        role = request.data.get('role', 'member')
        membership = GroupMember.objects.get(group=group, user_id=user_id)
        membership.role = role
        membership.save()
        return Response({'status': 'updated'})

    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        group = self.get_object()
        user_ids = group.fb_memberships.values_list('user_id', flat=True)
        posts = Post.objects.filter(author_id__in=user_ids).order_by('-created_at')[:20]
        return Response(PostSerializer(posts, many=True).data)


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'search':
            q = self.request.query_params.get('q', '')
            return Page.objects.filter(name__icontains=q)
        return Page.objects.all()

    def create(self, request):
        serializer = PageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post', 'delete'], url_path='follow')
    def follow(self, request, slug=None):
        page = self.get_object()
        if request.method == 'POST':
            page.follower_count += 1
            page.save()
            return Response({'following': True})
        page.follower_count = max(0, page.follower_count - 1)
        page.save()
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def posts(self, request, slug=None):
        page = self.get_object()
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=page.owner)
        return Response(serializer.data, status=201)


class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.action == 'list':
            return Message.objects.filter(sender=self.request.user).order_by('-created_at')
        tid = self.kwargs.get('thread_id')
        if tid:
            return Message.objects.filter(thread_id=tid)
        return Message.objects.all()

    def create(self, request):
        thread_id = uuid.uuid4()
        message = Message.objects.create(
            thread_id=thread_id,
            sender=request.user,
            body=request.data.get('body', ''),
            media_url=request.data.get('media', '')
        )
        return Response(MessageSerializer(message).data, status=201)

    def thread_messages(self, request, thread_id=None):
        messages = Message.objects.filter(thread_id=thread_id).order_by('created_at')
        return Response(MessageSerializer(messages, many=True).data)

    def thread_send_message(self, request, thread_id=None):
        message = Message.objects.create(
            thread_id=thread_id,
            sender=request.user,
            body=request.data.get('body', ''),
            media_url=request.data.get('media', '')
        )
        return Response(MessageSerializer(message).data, status=201)

    def thread_read(self, request, thread_id=None):
        return Response(status=204)

    def thread_typing(self, request, thread_id=None):
        return Response({'typing': False})


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


class AdminAuditLogView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response([])


class AdminUsersView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        q = request.query_params.get('q', '')
        users = User.objects.filter(email__icontains=q)[:50]
        return Response([{
            'id': str(u.id),
            'email': u.email,
            'fullName': u.full_name if hasattr(u, 'full_name') else u.email.split('@')[0],
            'isActive': u.is_active
        } for u in users])


class AdminPostHideView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        return Response(PostSerializer(post).data)
