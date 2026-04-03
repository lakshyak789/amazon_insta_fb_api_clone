import uuid
from django.db import models
from django.conf import settings


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('blocked', 'Blocked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_friend_requests_sent')
    addressee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_friend_requests_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facebook_friendships'
        unique_together = ('requester', 'addressee')


class Post(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('private', 'Private'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_posts')
    body = models.TextField(blank=True)
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='friends')
    media_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=20, blank=True)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facebook_posts'


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='fb_comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_comments')
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='fb_replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facebook_comments'


class Reaction(models.Model):
    TYPE_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    TARGET_TYPES = [('post', 'Post'), ('comment', 'Comment')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    target_id = models.UUIDField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reactions'
        unique_together = ('user', 'target_type', 'target_id')


class Group(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_owned_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_groups'


class GroupMember(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    ]
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('pending', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='fb_memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_group_members'
        unique_together = ('group', 'user')


class Page(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_pages')
    follower_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_pages'


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread_id = models.UUIDField()
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_sent_messages')
    body = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_messages'
        ordering = ['created_at']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('friend_request', 'Friend Request'),
        ('comment', 'Comment'),
        ('reaction', 'Reaction'),
        ('group_invite', 'Group Invite'),
        ('message', 'Message'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fb_notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    ref_type = models.CharField(max_length=20, blank=True)
    ref_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'facebook_notifications'
        ordering = ['-created_at']
