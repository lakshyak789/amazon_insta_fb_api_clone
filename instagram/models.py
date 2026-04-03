import uuid
from django.db import models
from django.conf import settings


class Follow(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('requested', 'Requested'),
        ('blocked', 'Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_following')
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_followers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_follows'
        unique_together = ('follower', 'followee')


class Media(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('carousel', 'Carousel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_media')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='image')
    urls = models.JSONField(default=dict)
    caption = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_media'
        ordering = ['-created_at']


class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_stories')
    media_url = models.URLField()
    expires_at = models.DateTimeField()
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_stories'


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='ig_comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_comments')
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='ig_replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_comments'


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_likes')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='ig_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_likes'
        unique_together = ('user', 'media')


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    usage_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'tags'


class MediaTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='media')

    class Meta:
        db_table = 'media_tags'
        unique_together = ('media', 'tag')


class DirectThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_direct_threads'


class DirectParticipant(models.Model):
    ROLE_CHOICES = [('member', 'Member'), ('admin', 'Admin')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DirectThread, on_delete=models.CASCADE, related_name='ig_participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_dm_participants')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')

    class Meta:
        db_table = 'instagram_direct_participants'
        unique_together = ('thread', 'user')


class DirectMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DirectThread, on_delete=models.CASCADE, related_name='ig_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_dm_sent')
    body = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_direct_messages'
        ordering = ['created_at']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
        ('dm', 'DM'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ig_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    ref_type = models.CharField(max_length=20, blank=True)
    ref_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_notifications'
        ordering = ['-created_at']
