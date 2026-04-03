from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from amazon.models import Category, Product, ProductImage, Inventory, Address
from facebook.models import Post, Group, Page, Comment, Reaction
from instagram.models import Media, Follow, Comment as IGComment, Like, Tag
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating users...')
        users = self.create_users()

        self.stdout.write('Creating Amazon data...')
        self.create_amazon_data(users)

        self.stdout.write('Creating Facebook data...')
        self.create_facebook_data(users)

        self.stdout.write('Creating Instagram data...')
        self.create_instagram_data(users)

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))

    def create_users(self):
        users = []
        emails = [
            ('alice@example.com', 'Alice', 'Johnson'),
            ('bob@example.com', 'Bob', 'Smith'),
            ('charlie@example.com', 'Charlie', 'Brown'),
            ('diana@example.com', 'Diana', 'Ross'),
            ('evan@example.com', 'Evan', 'Peters'),
        ]
        for i, (email, first, last) in enumerate(emails):
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'full_name': f'{first} {last}',
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('Password123!')
                user.save()
            users.append(user)
        return users

    def create_amazon_data(self, users):
        admin = users[0]

        categories = [
            ('Electronics', 'electronics', None),
            ('Laptops', 'laptops', 'electronics'),
            ('Phones', 'phones', 'electronics'),
            ('Clothing', 'clothing', None),
            ('Men', 'men', 'clothing'),
            ('Women', 'women', 'clothing'),
            ('Home & Garden', 'home-garden', None),
            ('Books', 'books', None),
        ]

        cat_objects = {}
        for name, slug, parent_slug in categories:
            parent = cat_objects.get(parent_slug)
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'parent': parent}
            )
            cat_objects[slug] = cat

        products_data = [
            ('MacBook Pro 16"', 'macbook-pro-16', 'Apple', 249900, 'electronics'),
            ('MacBook Air 13"', 'macbook-air-13', 'Apple', 99900, 'laptops'),
            ('ThinkPad X1 Carbon', 'thinkpad-x1-carbon', 'Lenovo', 149900, 'laptops'),
            ('iPhone 15 Pro', 'iphone-15-pro', 'Apple', 119900, 'phones'),
            ('Galaxy S24 Ultra', 'galaxy-s24-ultra', 'Samsung', 129900, 'phones'),
            ('Pixel 8 Pro', 'pixel-8-pro', 'Google', 99900, 'phones'),
            ('Nike Air Max', 'nike-air-max', 'Nike', 15999, 'men'),
            ('Adidas Ultraboost', 'adidas-ultraboost', 'Adidas', 18999, 'men'),
            ('Levi\'s 501 Jeans', 'levis-501-jeans', 'Levi\'s', 7999, 'men'),
            ('Ray-Ban Wayfarer', 'rayban-wayfarer', 'Ray-Ban', 15900, 'women'),
            ('Homer Garden Set', 'homer-garden-set', 'Homer', 29999, 'home-garden'),
            ('The Pragmatic Programmer', 'pragmatic-programmer', 'David Thomas', 4999, 'books'),
        ]

        for i, (title, slug, brand, price_cents, cat_slug) in enumerate(products_data):
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'sku': f'SKU-{i+1:04d}',
                    'brand': brand,
                    'price_cents': price_cents,
                    'category': cat_objects.get(cat_slug),
                    'description': f'This is a great {title} from {brand}. High quality product.',
                }
            )
            if created:
                ProductImage.objects.create(
                    product=product,
                    url=f'https://picsum.photos/seed/{slug}/800/800',
                    is_primary=True
                )
                Inventory.objects.create(
                    product=product,
                    quantity=random.randint(10, 200),
                    warehouse='Main Warehouse'
                )

        user = users[0]
        Address.objects.get_or_create(
            user=user,
            full_name='Alice Johnson',
            defaults={
                'label': 'Home',
                'line1': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA',
                'is_default': True
            }
        )

    def create_facebook_data(self, users):
        user1, user2, user3 = users[0], users[1], users[2]

        posts_data = [
            ('Just had an amazing coffee!', 'public', user1),
            ('Hello world! This is my first post.', 'public', user2),
            ('Beautiful day outside!', 'friends', user3),
            ('Working on a new project...', 'public', user1),
            ('Happy Friday everyone!', 'public', user2),
        ]

        for body, privacy, author in posts_data:
            post, created = Post.objects.get_or_create(
                author=author,
                body=body[:50],
                defaults={'privacy': privacy}
            )
            if created:
                post.body = body
                post.save()

        group, _ = Group.objects.get_or_create(
            slug='tech-talk',
            defaults={
                'name': 'Tech Talk',
                'description': 'A group for tech enthusiasts',
                'privacy': 'public',
                'owner': user1
            }
        )

        page, _ = Page.objects.get_or_create(
            slug='coding-tips',
            defaults={
                'name': 'Coding Tips',
                'category': 'Technology',
                'about': 'Daily coding tips and tricks',
                'owner': user2
            }
        )

        posts = Post.objects.all()[:3]
        for post in posts:
            Comment.objects.get_or_create(
                post=post,
                author=user2,
                body='Great post!'
            )
            Reaction.objects.get_or_create(
                user=user1,
                target_type='post',
                target_id=post.id,
                defaults={'type': 'like'}
            )

    def create_instagram_data(self, users):
        user1, user2, user3 = users[0], users[1], users[2]

        Follow.objects.get_or_create(
            follower=user1,
            followee=user2,
            defaults={'status': 'accepted'}
        )
        Follow.objects.get_or_create(
            follower=user2,
            followee=user1,
            defaults={'status': 'accepted'}
        )
        Follow.objects.get_or_create(
            follower=user3,
            followee=user1,
            defaults={'status': 'accepted'}
        )

        media_data = [
            ('Sunset vibes 🌅', 'image', user1),
            ('Morning coffee ☕', 'image', user2),
            ('Coding late night 💻', 'image', user1),
            ('Weekend vibes ✨', 'image', user3),
            ('New project launch! 🚀', 'image', user2),
        ]

        for caption, media_type, owner in media_data:
            urls = {
                'items': [{
                    'url': f'https://picsum.photos/seed/{caption[:10]}/800/800',
                    'width': 800,
                    'height': 800
                }]
            }
            media, created = Media.objects.get_or_create(
                owner=owner,
                caption=caption[:30],
                defaults={
                    'type': media_type,
                    'urls': urls,
                    'caption': caption
                }
            )
            if created:
                media.caption = caption
                media.save()

        tags_data = ['coding', 'python', 'django', 'webdev', 'programming']
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'usage_count': random.randint(10, 1000)}
            )

        media = Media.objects.first()
        if media:
            Like.objects.get_or_create(
                user=user2,
                media=media
            )
            IGComment.objects.get_or_create(
                media=media,
                user=user2,
                body='Amazing shot!'
            )
