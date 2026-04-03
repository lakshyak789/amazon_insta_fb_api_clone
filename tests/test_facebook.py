import uuid

import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from facebook.models import Friendship, Post, Comment, Reaction, Group, GroupMember, Page, Message, Notification

User = get_user_model()


@pytest.mark.django_db
class TestFacebookAuth:
    def test_register(self, api_client):
        response = api_client.post('/v1/auth/users/', {
            'email': 'fbuser@example.com',
            'password': 'FbPass123!',
            'full_name': 'FB User'
        })
        assert response.status_code == 201

    def test_login(self, api_client, user):
        response = api_client.post('/v1/auth/jwt/create', {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        })
        assert response.status_code == 200
        assert 'access' in response.data

    def test_get_me(self, authenticated_client, user):
        response = authenticated_client.get('/v1/me')
        assert response.status_code == 200

    def test_update_profile(self, authenticated_client, user):
        response = authenticated_client.patch('/v1/me', {
            'full_name': 'Updated Name',
            'bio': 'New bio'
        })
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserProfile:
    def test_get_user_profile(self, api_client, another_user):
        response = api_client.get(f'/v1/facebook/users/{another_user.id}/')
        assert response.status_code == 200

    def test_search_users(self, authenticated_client, another_user):
        response = authenticated_client.get('/v1/facebook/users/?q=another')
        assert response.status_code == 200


@pytest.mark.django_db
class TestFriendships:
    def test_send_friend_request(self, authenticated_client, another_user):
        response = authenticated_client.post('/v1/facebook/friends/requests/', {
            'toUserId': str(another_user.id)
        })
        assert response.status_code == 201

    def test_list_incoming_requests(self, authenticated_client, another_user):
        Friendship.objects.create(requester=another_user, addressee=authenticated_client.user, status='pending')
        response = authenticated_client.get('/v1/facebook/friends/requests/')
        assert response.status_code == 200

    def test_accept_friend_request(self, authenticated_client, another_user):
        friendship = Friendship.objects.create(requester=another_user, addressee=authenticated_client.user, status='pending')
        response = authenticated_client.post(f'/v1/facebook/friends/requests/{friendship.id}/accept/')
        assert response.status_code == 200
        friendship.refresh_from_db()
        assert friendship.status == 'accepted'

    def test_decline_friend_request(self, authenticated_client, another_user):
        friendship = Friendship.objects.create(requester=another_user, addressee=authenticated_client.user, status='pending')
        response = authenticated_client.post(f'/v1/facebook/friends/requests/{friendship.id}/decline/')
        assert response.status_code == 204

    def test_get_user_friends(self, api_client, user, another_user):
        Friendship.objects.create(requester=user, addressee=another_user, status='accepted')
        response = api_client.get(f'/v1/facebook/users/{user.id}/friends/')
        assert response.status_code == 200

    def test_unfriend(self, authenticated_client, user, another_user):
        Friendship.objects.create(requester=user, addressee=another_user, status='accepted')
        response = authenticated_client.delete(f'/v1/facebook/friends/{another_user.id}/')
        assert response.status_code == 204

    def test_block_user(self, authenticated_client, another_user):
        response = authenticated_client.post(f'/v1/facebook/users/{another_user.id}/block/')
        assert response.status_code == 200

    def test_unblock_user(self, authenticated_client, another_user):
        authenticated_client.post(f'/v1/facebook/users/{another_user.id}/block/')
        response = authenticated_client.delete(f'/v1/facebook/users/{another_user.id}/block/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestPosts:
    def test_create_post(self, authenticated_client):
        response = authenticated_client.post('/v1/facebook/posts/', {
            'body': 'Hello World!',
            'privacy': 'public'
        })
        assert response.status_code == 201

    def test_get_post(self, api_client, user):
        post = Post.objects.create(author=user, body='Test Post', privacy='public')
        response = api_client.get(f'/v1/facebook/posts/{post.id}/')
        assert response.status_code == 200
        assert response.data['body'] == 'Test Post'

    def test_update_post(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Original', privacy='public')
        response = authenticated_client.patch(f'/v1/facebook/posts/{post.id}/', {
            'body': 'Updated'
        })
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.body == 'Updated'

    def test_delete_post(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='To Delete', privacy='public')
        response = authenticated_client.delete(f'/v1/facebook/posts/{post.id}/')
        assert response.status_code == 204

    def test_get_user_posts(self, api_client, user):
        Post.objects.create(author=user, body='User Post', privacy='public')
        response = api_client.get(f'/v1/facebook/users/{user.id}/posts/')
        assert response.status_code == 200

    def test_feed(self, authenticated_client, user):
        Post.objects.create(author=user, body='Feed Post', privacy='public')
        response = authenticated_client.get('/v1/facebook/posts/feed/')
        assert response.status_code == 200

    def test_trending_posts(self, api_client, user):
        Post.objects.create(author=user, body='Trending Post', privacy='public', like_count=10)
        response = api_client.get('/v1/facebook/posts/trending/')
        assert response.status_code == 200

    def test_search_posts(self, authenticated_client):
        Post.objects.create(author=authenticated_client.user, body='Search Me', privacy='public')
        response = authenticated_client.get('/v1/facebook/search/posts/?q=Search')
        assert response.status_code == 200

    def test_share_post(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Original', privacy='public')
        response = authenticated_client.post(f'/v1/facebook/posts/{post.id}/share/')
        assert response.status_code == 200

    def test_report_post(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Report Me', privacy='public')
        response = authenticated_client.post(f'/v1/facebook/posts/{post.id}/report/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestComments:
    def test_create_comment(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Post with Comment', privacy='public')
        response = authenticated_client.post(f'/v1/facebook/posts/{post.id}/comments/', {
            'body': 'Great post!'
        })
        assert response.status_code == 201
        post.refresh_from_db()
        assert post.comment_count == 1

    def test_list_comments(self, api_client, user):
        post = Post.objects.create(author=user, body='Post', privacy='public')
        Comment.objects.create(post=post, author=user, body='Comment')
        response = api_client.get(f'/v1/facebook/posts/{post.id}/comments/')
        assert response.status_code == 200

    def test_update_comment(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Post', privacy='public')
        comment = Comment.objects.create(post=post, author=user, body='Original')
        response = authenticated_client.patch(f'/v1/facebook/comments/{comment.id}/', {
            'body': 'Updated'
        })
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.body == 'Updated'

    def test_delete_comment(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Post', privacy='public')
        comment = Comment.objects.create(post=post, author=user, body='To Delete')
        response = authenticated_client.delete(f'/v1/facebook/comments/{comment.id}/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestReactions:
    def test_react_to_post(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='React Post', privacy='public')
        response = authenticated_client.post(f'/v1/facebook/posts/{post.id}/reactions/', {
            'type': 'like'
        })
        assert response.status_code == 200

    def test_remove_reaction(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Remove React', privacy='public')
        Reaction.objects.create(user=authenticated_client.user, target_type='post', target_id=post.id, type='like')
        response = authenticated_client.delete(f'/v1/facebook/posts/{post.id}/reactions/')
        assert response.status_code == 204

    def test_get_reactions(self, api_client, user):
        post = Post.objects.create(author=user, body='Reactions', privacy='public')
        Reaction.objects.create(user=user, target_type='post', target_id=post.id, type='love')
        response = api_client.get(f'/v1/facebook/posts/{post.id}/reactions/')
        assert response.status_code == 200

    def test_react_to_comment(self, authenticated_client, user):
        post = Post.objects.create(author=user, body='Post', privacy='public')
        comment = Comment.objects.create(post=post, author=user, body='Comment')
        response = authenticated_client.post(f'/v1/facebook/comments/{comment.id}/reactions/', {
            'type': 'haha'
        })
        assert response.status_code == 200


@pytest.mark.django_db
class TestGroups:
    def test_create_group(self, authenticated_client):
        response = authenticated_client.post('/v1/facebook/groups/', {
            'name': 'Test Group',
            'slug': 'test-group',
            'description': 'A test group',
            'privacy': 'public'
        })
        assert response.status_code == 201

    def test_list_groups(self, api_client, user):
        Group.objects.create(name='Public Group', slug='public-group', privacy='public', owner=user)
        response = api_client.get('/v1/facebook/groups/')
        assert response.status_code == 200

    def test_get_group(self, api_client, user):
        group = Group.objects.create(name='My Group', slug='my-group', privacy='public', owner=user)
        response = api_client.get(f'/v1/facebook/groups/{group.slug}/')
        assert response.status_code == 200

    def test_join_group(self, authenticated_client, user):
        group = Group.objects.create(name='Join Group', slug='join-group', privacy='public', owner=user)
        response = authenticated_client.post(f'/v1/facebook/groups/{group.slug}/join/')
        assert response.status_code == 200

    def test_leave_group(self, authenticated_client, user):
        group = Group.objects.create(name='Leave Group', slug='leave-group', privacy='public', owner=user)
        GroupMember.objects.create(group=group, user=authenticated_client.user)
        response = authenticated_client.post(f'/v1/facebook/groups/{group.slug}/leave/')
        assert response.status_code == 204

    def test_group_posts(self, api_client, user):
        group = Group.objects.create(name='Posts Group', slug='posts-group', privacy='public', owner=user)
        Post.objects.create(author=user, body='Group Post', privacy='public')
        response = api_client.get(f'/v1/facebook/groups/{group.slug}/posts/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestPages:
    def test_create_page(self, authenticated_client):
        response = authenticated_client.post('/v1/facebook/pages/', {
            'name': 'My Page',
            'slug': 'my-page',
            'about': 'About my page',
            'category': 'Technology'
        })
        assert response.status_code == 201

    def test_list_pages(self, authenticated_client, user):
        Page.objects.create(name='List Page', slug='list-page', owner=user)
        response = authenticated_client.get('/v1/facebook/pages/')
        assert response.status_code == 200

    def test_get_page(self, api_client, user):
        page = Page.objects.create(name='Get Page', slug='get-page', owner=user)
        response = api_client.get(f'/v1/facebook/pages/{page.slug}/')
        assert response.status_code == 200

    def test_follow_page(self, authenticated_client, user):
        page = Page.objects.create(name='Follow Page', slug='follow-page', owner=user)
        response = authenticated_client.post(f'/v1/facebook/pages/{page.slug}/follow/')
        assert response.status_code == 200
        page.refresh_from_db()
        assert page.follower_count == 1

    def test_unfollow_page(self, authenticated_client, user):
        page = Page.objects.create(name='Unfollow Page', slug='unfollow-page', owner=user, follower_count=1)
        response = authenticated_client.delete(f'/v1/facebook/pages/{page.slug}/follow/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestMessaging:
    def test_create_thread(self, authenticated_client, another_user):
        response = authenticated_client.post('/v1/facebook/threads/', {
            'participantIds': [str(another_user.id)]
        })
        assert response.status_code == 201

    def test_list_threads(self, authenticated_client):
        Message.objects.create(thread_id=uuid.uuid4(), sender=authenticated_client.user, body='Thread msg')
        response = authenticated_client.get('/v1/facebook/threads/')
        assert response.status_code == 200

    def test_send_message(self, authenticated_client, another_user):
        thread = Message.objects.create(thread_id=uuid.uuid4(), sender=authenticated_client.user, body='First')
        response = authenticated_client.post(f'/v1/facebook/threads/{thread.thread_id}/messages/', {
            'body': 'Hello!'
        })
        assert response.status_code == 201

    def test_mark_read(self, authenticated_client):
        thread = Message.objects.create(thread_id=uuid.uuid4(), sender=authenticated_client.user, body='Read me')
        response = authenticated_client.post(f'/v1/facebook/threads/{thread.thread_id}/read/')
        assert response.status_code == 204

    def test_typing_indicator(self, authenticated_client):
        thread = Message.objects.create(thread_id=uuid.uuid4(), sender=authenticated_client.user, body='Typing')
        response = authenticated_client.get(f'/v1/facebook/threads/{thread.thread_id}/typing/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestNotifications:
    def test_list_notifications(self, authenticated_client):
        Notification.objects.create(user=authenticated_client.user, type='friend_request')
        response = authenticated_client.get('/v1/facebook/notifications/')
        assert response.status_code == 200

    def test_mark_notification_read(self, authenticated_client):
        notif = Notification.objects.create(user=authenticated_client.user, type='comment')
        response = authenticated_client.post(f'/v1/facebook/notifications/{notif.id}/read/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestAdmin:
    def test_admin_audit_logs(self, admin_client):
        response = admin_client.get('/v1/facebook/admin/audit_logs/')
        assert response.status_code == 200

    def test_admin_list_users(self, admin_client):
        response = admin_client.get('/v1/facebook/admin/users/')
        assert response.status_code == 200

    def test_admin_hide_post(self, admin_client, user):
        post = Post.objects.create(author=user, body='Hide Me', privacy='public')
        response = admin_client.post(f'/v1/facebook/admin/posts/{post.id}/hide/')
        assert response.status_code == 200
