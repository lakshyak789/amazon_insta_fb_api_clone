from rest_framework import serializers
from core.serializers import UserSerializer
from .models import Friendship, Post, Comment, Reaction, Group, GroupMember, Page, Message, Notification


class FriendshipSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    addressee = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ('id', 'requester', 'addressee', 'status', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    counts = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'author', 'body', 'privacy', 'media', 'counts', 'createdAt')

    def get_counts(self, obj):
        return {'likes': obj.like_count, 'comments': obj.comment_count}

    def get_media(self, obj):
        return {'url': obj.media_url, 'type': obj.media_type} if obj.media_url else {'url': None, 'type': None}

    def get_createdAt(self, obj):
        return obj.created_at.isoformat()


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'author', 'body', 'parent_id', 'createdAt')

    def get_createdAt(self, obj):
        return obj.created_at.isoformat()


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ('id', 'user_id', 'target_type', 'target_id', 'type', 'created_at')


class GroupSerializer(serializers.ModelSerializer):
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'slug', 'description', 'privacy', 'owner_id', 'created_at')


class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ('id', 'user', 'role', 'status', 'created_at')


class PageSerializer(serializers.ModelSerializer):
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'slug', 'category', 'about', 'owner_id', 'follower_count', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'thread_id', 'sender', 'body', 'media_url', 'created_at')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'type', 'ref_type', 'ref_id', 'is_read', 'created_at')


class ThreadSerializer(serializers.Serializer):
    thread_id = serializers.UUIDField()
    participants = UserSerializer(many=True)
    last_message = MessageSerializer()
