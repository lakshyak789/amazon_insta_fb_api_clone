from rest_framework import serializers
from core.serializers import UserSerializer
from .models import Follow, Media, Story, Comment, Like, Tag, MediaTag, DirectThread, DirectParticipant, DirectMessage, Notification


class MediaSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('id', 'owner', 'type', 'urls', 'caption', 'location', 'counts', 'createdAt')

    def get_owner(self, obj):
        return {'id': str(obj.owner.id), 'username': getattr(obj.owner, 'username', obj.owner.email.split('@')[0])}

    def get_counts(self, obj):
        return {'likes': obj.like_count, 'comments': obj.comment_count}

    def get_createdAt(self, obj):
        return obj.created_at.isoformat()


class MediaListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    counts = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ('id', 'owner', 'type', 'urls', 'counts', 'createdAt')

    def get_owner(self, obj):
        return {'id': str(obj.owner.id), 'username': getattr(obj.owner, 'username', obj.owner.email.split('@')[0])}

    def get_counts(self, obj):
        return {'likes': obj.like_count, 'comments': obj.comment_count}

    def get_createdAt(self, obj):
        return obj.created_at.isoformat()


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'body', 'parent_id', 'createdAt')

    def get_user(self, obj):
        return {'id': str(obj.user.id), 'username': getattr(obj.user, 'username', obj.user.email.split('@')[0])}

    def get_createdAt(self, obj):
        return obj.created_at.isoformat()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('id', 'follower_id', 'followee_id', 'status', 'created_at')


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user_id', 'media_id', 'created_at')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'usage_count')


class StorySerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ('id', 'owner', 'media_url', 'expires_at', 'view_count', 'created_at')

    def get_owner(self, obj):
        return {'id': str(obj.owner.id), 'username': getattr(obj.owner, 'username', obj.owner.email.split('@')[0])}


class DirectMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = DirectMessage
        fields = ('id', 'thread_id', 'sender', 'body', 'media_url', 'created_at')

    def get_sender(self, obj):
        return {'id': str(obj.sender.id), 'username': getattr(obj.sender, 'username', obj.sender.email.split('@')[0])}


class DirectThreadSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = DirectThread
        fields = ('id', 'is_group', 'participants', 'last_message', 'created_at')

    def get_participants(self, obj):
        participants = obj.ig_participants.all()
        return [{'id': str(p.user.id), 'username': getattr(p.user, 'username', p.user.email.split('@')[0])} for p in participants]

    def get_last_message(self, obj):
        msg = obj.ig_messages.last()
        return DirectMessageSerializer(msg).data if msg else None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'type', 'ref_type', 'ref_id', 'is_read', 'created_at')
