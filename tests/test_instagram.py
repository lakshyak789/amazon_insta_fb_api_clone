import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from instagram.models import Follow, Media, Story, Comment, Like, Tag, MediaTag, DirectThread, DirectParticipant, DirectMessage, Notification

User = get_user_model()


@pytest.mark.django_db
class TestInstagramAuth:
    def test_register(self, api_client):
        response = api_client.post('/v1/auth/users/', {
            'email': 'iguser@example.com',
            'password': 'IgPass123!',
            'username': 'iguser',
            'full_name': 'IG User'
        })
        assert response.status_code == 201

    def test_login(self, api_client, user):
        user.username = 'testuser'
        user.save()
        response = api_client.post('/v1/auth/jwt/create', {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        })
        assert response.status_code == 200
        assert 'access' in response.data

    def test_get_me(self, authenticated_client, user):
        user.username = 'meuser'
        user.save()
        response = authenticated_client.get('/v1/me')
        assert response.status_code == 200

    def test_update_profile(self, authenticated_client, user):
        user.username = 'updateuser'
        user.save()
        response = authenticated_client.patch('/v1/me', {
            'full_name': 'Updated Name',
            'bio': 'New bio'
        })
        assert response.status_code == 200


@pytest.mark.django_db
class TestInstagramUserProfile:
    def test_get_user_by_username(self, api_client):
        user = User.objects.create_user(
            email='profile@example.com',
            password='Pass123!',
            username='profileuser',
            full_name='Profile User'
        )
        response = api_client.get(f'/v1/instagram/users/{user.username}/')
        assert response.status_code == 200

    def test_search_users(self, api_client):
        User.objects.create_user(
            email='search@example.com',
            password='Pass123!',
            username='searchuser',
            full_name='Search User'
        )
        response = api_client.get('/v1/instagram/users/?q=search')
        assert response.status_code == 200


@pytest.mark.django_db
class TestFollows:
    def test_follow_user(self, authenticated_client, another_user):
        response = authenticated_client.post(f'/v1/instagram/users/{another_user.id}/follow/')
        assert response.status_code == 200

    def test_unfollow_user(self, authenticated_client, another_user):
        Follow.objects.create(follower=authenticated_client.user, followee=another_user)
        response = authenticated_client.delete(f'/v1/instagram/users/{another_user.id}/follow/')
        assert response.status_code == 204

    def test_get_followers(self, api_client, user, another_user):
        Follow.objects.create(follower=user, followee=another_user)
        response = api_client.get(f'/v1/instagram/users/{another_user.id}/followers/')
        assert response.status_code == 200

    def test_get_following(self, api_client, user, another_user):
        Follow.objects.create(follower=user, followee=another_user)
        response = api_client.get(f'/v1/instagram/users/{user.id}/following/')
        assert response.status_code == 200

    def test_follow_suggestions(self, authenticated_client):
        User.objects.create_user(email='suggest@example.com', password='Pass123!', username='suggest')
        response = authenticated_client.get('/v1/instagram/me/follow_suggestions/')
        assert response.status_code == 200

    def test_approve_follow_request(self, authenticated_client, another_user):
        follow = Follow.objects.create(
            follower=another_user,
            followee=authenticated_client.user,
            status='requested'
        )
        response = authenticated_client.post(f'/v1/instagram/follow_requests/{follow.id}/', {
            'action': 'approve'
        })
        assert response.status_code == 204

    def test_decline_follow_request(self, authenticated_client, another_user):
        follow = Follow.objects.create(
            follower=another_user,
            followee=authenticated_client.user,
            status='requested'
        )
        response = authenticated_client.post(f'/v1/instagram/follow_requests/{follow.id}/', {
            'action': 'decline'
        })
        assert response.status_code == 204


@pytest.mark.django_db
class TestMedia:
    def test_upload_media(self, authenticated_client):
        response = authenticated_client.post('/v1/instagram/media/', {
            'type': 'image',
            'urls': {'items': [{'url': 'http://example.com/img.jpg', 'width': 1080, 'height': 1080}]},
            'caption': 'My photo'
        }, format='json')
        assert response.status_code == 201

    def test_get_media(self, api_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = api_client.get(f'/v1/instagram/media/{media.id}/')
        assert response.status_code == 200

    def test_update_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]},
            caption='Original'
        )
        response = authenticated_client.patch(f'/v1/instagram/media/{media.id}/', {
            'caption': 'Updated caption'
        })
        assert response.status_code == 200
        media.refresh_from_db()
        assert media.caption == 'Updated caption'

    def test_delete_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.delete(f'/v1/instagram/media/{media.id}/')
        assert response.status_code == 204

    def test_archive_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.post(f'/v1/instagram/media/{media.id}/archive/')
        assert response.status_code == 200
        media.refresh_from_db()
        assert media.is_archived is True

    def test_unarchive_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]},
            is_archived=True
        )
        response = authenticated_client.delete(f'/v1/instagram/media/{media.id}/archive/')
        assert response.status_code == 200
        media.refresh_from_db()
        assert media.is_archived is False

    def test_like_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.post(f'/v1/instagram/media/{media.id}/like/')
        assert response.status_code == 200
        assert response.data['liked'] is True

    def test_unlike_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        Like.objects.create(user=authenticated_client.user, media=media)
        media.like_count = 1
        media.save()
        response = authenticated_client.delete(f'/v1/instagram/media/{media.id}/like/')
        assert response.status_code == 200
        assert response.data['liked'] is False

    def test_get_likes(self, api_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        Like.objects.create(user=user, media=media)
        response = api_client.get(f'/v1/instagram/media/{media.id}/likes/')
        assert response.status_code == 200

    def test_get_user_media(self, api_client, user):
        Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = api_client.get(f'/v1/instagram/users/{user.id}/media/')
        assert response.status_code == 200

    def test_feed(self, authenticated_client, user):
        Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.get('/v1/instagram/feed/')
        assert response.status_code == 200

    def test_explore(self, api_client, user):
        Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]},
            like_count=100
        )
        response = api_client.get('/v1/instagram/explore/')
        assert response.status_code == 200

    def test_report_media(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.post(f'/v1/instagram/media/{media.id}/report/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestComments:
    def test_create_comment(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        response = authenticated_client.post(f'/v1/instagram/media/{media.id}/comments/', {
            'body': 'Great photo!'
        })
        assert response.status_code == 201
        media.refresh_from_db()
        assert media.comment_count == 1

    def test_list_comments(self, api_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        Comment.objects.create(media=media, user=user, body='Comment')
        response = api_client.get(f'/v1/instagram/media/{media.id}/comments/')
        assert response.status_code == 200

    def test_update_comment(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        comment = Comment.objects.create(media=media, user=user, body='Original')
        response = authenticated_client.patch(f'/v1/instagram/comments/{comment.id}/', {
            'body': 'Updated'
        })
        assert response.status_code == 200
        comment.refresh_from_db()
        assert comment.body == 'Updated'

    def test_delete_comment(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        comment = Comment.objects.create(media=media, user=user, body='To Delete')
        response = authenticated_client.delete(f'/v1/instagram/comments/{comment.id}/')
        assert response.status_code == 204

    def test_report_comment(self, authenticated_client, user):
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        comment = Comment.objects.create(media=media, user=user, body='Report me')
        response = authenticated_client.post(f'/v1/instagram/comments/{comment.id}/report/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestMentions:
    def test_get_mentions(self, authenticated_client):
        response = authenticated_client.get('/v1/instagram/mentions/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestStories:
    def test_create_story(self, authenticated_client):
        response = authenticated_client.post('/v1/instagram/stories/', {
            'url': 'http://example.com/story.jpg',
            'expiresIn': 86400
        })
        assert response.status_code == 201

    def test_get_combined_stories(self, authenticated_client, user):
        from django.utils import timezone
        from datetime import timedelta
        Story.objects.create(
            owner=user,
            media_url='http://example.com/story.jpg',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = authenticated_client.get('/v1/instagram/stories/combined/')
        assert response.status_code == 200

    def test_get_user_stories(self, api_client, user):
        from django.utils import timezone
        from datetime import timedelta
        Story.objects.create(
            owner=user,
            media_url='http://example.com/story.jpg',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = api_client.get(f'/v1/instagram/users/{user.id}/stories/')
        assert response.status_code == 200

    def test_view_story(self, authenticated_client, user):
        from django.utils import timezone
        from datetime import timedelta
        story = Story.objects.create(
            owner=user,
            media_url='http://example.com/story.jpg',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = authenticated_client.post(f'/v1/instagram/stories/{story.id}/view/')
        assert response.status_code == 200
        story.refresh_from_db()
        assert story.view_count == 1

    def test_delete_story(self, authenticated_client, user):
        from django.utils import timezone
        from datetime import timedelta
        story = Story.objects.create(
            owner=user,
            media_url='http://example.com/story.jpg',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = authenticated_client.delete(f'/v1/instagram/stories/{story.id}/')
        assert response.status_code == 204

    def test_get_story_viewers(self, authenticated_client, user):
        from django.utils import timezone
        from datetime import timedelta
        story = Story.objects.create(
            owner=user,
            media_url='http://example.com/story.jpg',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        response = authenticated_client.get(f'/v1/instagram/stories/{story.id}/viewers/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestTags:
    def test_search_tags(self, api_client):
        Tag.objects.create(name='python', usage_count=100)
        response = api_client.get('/v1/instagram/tags/?q=py')
        assert response.status_code == 200

    def test_create_tag_admin(self, admin_client):
        response = admin_client.post('/v1/instagram/tags/', {
            'name': 'django'
        })
        assert response.status_code == 201

    def test_get_tag_media(self, api_client, user):
        tag = Tag.objects.create(name='photo', usage_count=10)
        media = Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]}
        )
        MediaTag.objects.create(media=media, tag=tag)
        response = api_client.get(f'/v1/instagram/tags/{tag.id}/media/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestSearch:
    def test_search_users(self, api_client):
        User.objects.create_user(
            email='john@example.com',
            password='Pass123!',
            username='johndoe'
        )
        response = api_client.get('/v1/instagram/search/?q=john&type=user')
        assert response.status_code == 200

    def test_search_tags(self, api_client):
        Tag.objects.create(name='coding', usage_count=50)
        response = api_client.get('/v1/instagram/search/?q=cod&type=tag')
        assert response.status_code == 200


@pytest.mark.django_db
class TestPlaces:
    def test_search_places(self, api_client, user):
        Media.objects.create(
            owner=user,
            type='image',
            urls={'items': [{'url': 'http://example.com/img.jpg'}]},
            location='New York'
        )
        response = api_client.get('/v1/instagram/places/?q=New')
        assert response.status_code == 200


@pytest.mark.django_db
class TestDirectMessages:
    def test_create_thread(self, authenticated_client, another_user):
        response = authenticated_client.post('/v1/instagram/dm/threads/', {
            'participantIds': [str(another_user.id)]
        })
        assert response.status_code == 201

    def test_list_threads(self, authenticated_client):
        thread = DirectThread.objects.create()
        DirectParticipant.objects.create(thread=thread, user=authenticated_client.user)
        response = authenticated_client.get('/v1/instagram/dm/threads/')
        assert response.status_code == 200

    def test_get_thread_messages(self, authenticated_client, another_user):
        thread = DirectThread.objects.create()
        DirectParticipant.objects.create(thread=thread, user=authenticated_client.user)
        DirectParticipant.objects.create(thread=thread, user=another_user)
        DirectMessage.objects.create(
            thread=thread,
            sender=authenticated_client.user,
            body='Hello'
        )
        response = authenticated_client.get(f'/v1/instagram/dm/threads/{thread.id}/messages/')
        assert response.status_code == 200

    def test_send_message(self, authenticated_client, another_user):
        thread = DirectThread.objects.create()
        DirectParticipant.objects.create(thread=thread, user=authenticated_client.user)
        DirectParticipant.objects.create(thread=thread, user=another_user)
        response = authenticated_client.post(f'/v1/instagram/dm/threads/{thread.id}/messages/send/', {
            'body': 'Hi there!'
        })
        assert response.status_code == 201

    def test_mark_thread_read(self, authenticated_client):
        thread = DirectThread.objects.create()
        DirectParticipant.objects.create(thread=thread, user=authenticated_client.user)
        response = authenticated_client.post(f'/v1/instagram/dm/threads/{thread.id}/read/')
        assert response.status_code == 204

    def test_leave_thread(self, authenticated_client):
        thread = DirectThread.objects.create()
        DirectParticipant.objects.create(thread=thread, user=authenticated_client.user)
        response = authenticated_client.post(f'/v1/instagram/dm/threads/{thread.id}/leave/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestInstagramNotifications:
    def test_list_notifications(self, authenticated_client):
        Notification.objects.create(
            user=authenticated_client.user,
            type='like',
            ref_type='media'
        )
        response = authenticated_client.get('/v1/instagram/notifications/')
        assert response.status_code == 200

    def test_mark_notification_read(self, authenticated_client):
        notif = Notification.objects.create(
            user=authenticated_client.user,
            type='comment'
        )
        response = authenticated_client.post(f'/v1/instagram/notifications/{notif.id}/read/')
        assert response.status_code == 204


@pytest.mark.django_db
class TestInstagramAdmin:
    def test_admin_list_users(self, admin_client):
        response = admin_client.get('/v1/instagram/admin/users/')
        assert response.status_code == 200

    def test_admin_verify_user(self, admin_client, another_user):
        response = admin_client.patch(f'/v1/instagram/admin/users/{another_user.id}/verify/', {
            'is_verified': True
        })
        assert response.status_code == 200
        another_user.refresh_from_db()
        assert another_user.is_verified is True

    def test_admin_audit_logs(self, admin_client):
        response = admin_client.get('/v1/instagram/admin/audit_logs/')
        assert response.status_code == 200

    def test_admin_trending_tags(self, admin_client):
        Tag.objects.create(name='trending', usage_count=500)
        response = admin_client.get('/v1/instagram/admin/trends/tags/')
        assert response.status_code == 200

    def test_admin_abuse_reports(self, admin_client):
        response = admin_client.get('/v1/instagram/admin/abuse/reports/')
        assert response.status_code == 200

    def test_admin_resolve_abuse_report(self, admin_client):
        response = admin_client.post('/v1/instagram/admin/abuse/reports/some-id/resolve/', {
            'action': 'warned'
        })
        assert response.status_code == 200
