from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from instagram.models import Media, Story, Comment, Tag, DirectThread, DirectMessage, Follow
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Add sample Instagram data'

    def handle(self, *args, **options):
        self.stdout.write('Creating Instagram users...')
        
        user1, created = User.objects.get_or_create(
            email='instauser1@test.com',
            defaults={'username': 'instauser1', 'full_name': 'John Doe', 'is_verified': True}
        )
        if created:
            user1.set_password('Test123456')
            user1.save()
        
        user2, created = User.objects.get_or_create(
            email='instauser2@test.com',
            defaults={'username': 'instauser2', 'full_name': 'Jane Smith', 'is_verified': False}
        )
        if created:
            user2.set_password('Test123456')
            user2.save()
            
        user3, created = User.objects.get_or_create(
            email='instauser3@test.com',
            defaults={'username': 'instauser3', 'full_name': 'Bob Wilson', 'is_verified': True}
        )
        if created:
            user3.set_password('Test123456')
            user3.save()

        self.stdout.write(self.style.SUCCESS(f'Created users: {user1.username}, {user2.username}, {user3.username}'))

        Follow.objects.get_or_create(follower=user1, followee=user2, defaults={'status': 'accepted'})
        Follow.objects.get_or_create(follower=user1, followee=user3, defaults={'status': 'accepted'})
        Follow.objects.get_or_create(follower=user2, followee=user1, defaults={'status': 'accepted'})
        
        self.stdout.write(self.style.SUCCESS('Created follows'))

        tag1, _ = Tag.objects.get_or_create(name='nature', defaults={'usage_count': 5})
        tag2, _ = Tag.objects.get_or_create(name='photography', defaults={'usage_count': 3})
        tag3, _ = Tag.objects.get_or_create(name='travel', defaults={'usage_count': 8})
        
        self.stdout.write(self.style.SUCCESS('Created tags'))

        media1 = Media.objects.create(
            owner=user1, type='image',
            urls={'items': [{'url': 'http://example.com/img1.jpg', 'width': 1080, 'height': 1080}]},
            caption='Beautiful sunset! #nature #travel', like_count=5, comment_count=2, is_archived=False
        )
        from instagram.models import MediaTag
        MediaTag.objects.create(media=media1, tag=tag1)
        MediaTag.objects.create(media=media1, tag=tag3)
        
        media2 = Media.objects.create(
            owner=user2, type='image',
            urls={'items': [{'url': 'http://example.com/img2.jpg', 'width': 1080, 'height': 1350}]},
            caption='Morning coffee #photography', like_count=3, comment_count=1, is_archived=False
        )
        MediaTag.objects.create(media=media2, tag=tag2)
        
        media3 = Media.objects.create(
            owner=user3, type='video',
            urls={'items': [{'url': 'http://example.com/vid1.mp4', 'width': 1080, 'height': 1920}]},
            caption='Amazing view! #travel #nature', like_count=10, comment_count=4, is_archived=False
        )
        MediaTag.objects.create(media=media3, tag=tag1)
        MediaTag.objects.create(media=media3, tag=tag2)
        MediaTag.objects.create(media=media3, tag=tag3)

        self.stdout.write(self.style.SUCCESS(f'Created {Media.objects.count()} media posts'))

        comment1 = Comment.objects.create(user=user2, media=media1, body='Amazing photo!')
        comment2 = Comment.objects.create(user=user3, media=media1, body='Love the colors!')
        comment3 = Comment.objects.create(user=user1, media=media2, body='Nice brew!')

        self.stdout.write(self.style.SUCCESS(f'Created {Comment.objects.count()} comments'))

        story1 = Story.objects.create(owner=user1, media_url='http://example.com/story1.jpg', expires_at=timezone.now() + timedelta(hours=24), view_count=15)
        story2 = Story.objects.create(owner=user2, media_url='http://example.com/story2.jpg', expires_at=timezone.now() + timedelta(hours=24), view_count=8)
        story3 = Story.objects.create(owner=user3, media_url='http://example.com/story3.jpg', expires_at=timezone.now() + timedelta(hours=24), view_count=25)

        self.stdout.write(self.style.SUCCESS(f'Created {Story.objects.count()} stories'))

        from instagram.models import DirectParticipant, DirectThread, DirectMessage
        thread1 = DirectThread.objects.create(is_group=False)
        DirectParticipant.objects.create(thread=thread1, user=user1)
        DirectParticipant.objects.create(thread=thread1, user=user2)
        message1 = DirectMessage.objects.create(thread=thread1, sender=user1, body='Hey! How are you?')
        
        thread2 = DirectThread.objects.create(is_group=True)
        DirectParticipant.objects.create(thread=thread2, user=user1)
        DirectParticipant.objects.create(thread=thread2, user=user2)
        DirectParticipant.objects.create(thread=thread2, user=user3)

        self.stdout.write(self.style.SUCCESS(f'Created {DirectThread.objects.count()} DM threads'))

        self.stdout.write(self.style.SUCCESS('\nInstagram sample data created!'))
        self.stdout.write(self.style.SUCCESS('Test Users:'))
        self.stdout.write(self.style.SUCCESS('  instauser1@test.com / Test123456'))
        self.stdout.write(self.style.SUCCESS('  instauser2@test.com / Test123456'))
        self.stdout.write(self.style.SUCCESS('  instauser3@test.com / Test123456'))