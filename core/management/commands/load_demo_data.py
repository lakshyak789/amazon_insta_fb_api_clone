from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from facebook.models import Post, Comment, Reaction, Friendship, Group, GroupMember, Page, Message, Notification
from amazon.models import Address, Category, Product, ProductImage, Inventory, Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, Payment, Review, AuditLog
from instagram.models import Follow, Media, Story, Comment as IGComment, Like, Tag, MediaTag, DirectThread, DirectParticipant, DirectMessage, Notification as IGNotification
from django.utils.text import slugify
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Load demo data including admin user'

    def handle(self, *args, **options):
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'username': 'admin',
                'full_name': 'Admin User',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
                'role': 'admin',
            }
        )
        if created:
            admin.set_password('Admin123456!')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin: admin@test.com / Admin123456!'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin already exists'))

        # Create regular user 1
        user1, created = User.objects.get_or_create(
            email='user1@test.com',
            defaults={
                'username': 'user1',
                'full_name': 'Test User 1',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': True,
                'role': 'customer',
            }
        )
        if created:
            user1.set_password('User123456!')
            user1.save()
            self.stdout.write(self.style.SUCCESS(f'Created user1: user1@test.com / User123456!'))
        else:
            self.stdout.write(self.style.WARNING(f'User1 already exists'))

        # Create regular user 2
        user2, created = User.objects.get_or_create(
            email='user2@test.com',
            defaults={
                'username': 'user2',
                'full_name': 'Test User 2',
                'is_staff': False,
                'is_superuser': False,
                'is_verified': False,
                'role': 'customer',
            }
        )
        if created:
            user2.set_password('User123456!')
            user2.save()
            self.stdout.write(self.style.SUCCESS(f'Created user2: user2@test.com / User123456!'))
        else:
            self.stdout.write(self.style.WARNING(f'User2 already exists'))

        # Load Facebook demo data
        self.load_facebook_demo_data(admin, user1, user2)
        
        # Load Amazon demo data
        self.load_amazon_demo_data(admin, user1, user2)
        
        # Load Instagram demo data
        self.load_instagram_demo_data(admin, user1, user2)

        self.stdout.write(self.style.SUCCESS('\nDemo data loaded successfully!'))

    def load_facebook_demo_data(self, admin, user1, user2):
        """Load Facebook-related demo data"""
        
        # Create friendships
        self.stdout.write('\nCreating friendships...')
        friendship1, created = Friendship.objects.get_or_create(
            requester=user1,
            addressee=user2,
            defaults={'status': 'accepted'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created friendship: user1 -> user2'))
        
        friendship2, created = Friendship.objects.get_or_create(
            requester=admin,
            addressee=user1,
            defaults={'status': 'accepted'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created friendship: admin -> user1'))

        # Create posts
        self.stdout.write('\nCreating posts...')
        post1, created = Post.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'author': admin,
                'body': 'Welcome to our Facebook clone! This is a demo post from the admin user. #social #demo',
                'privacy': 'public',
                'like_count': 5,
                'comment_count': 2
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created admin post'))

        post2, created = Post.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'author': user1,
                'body': 'Excited to be part of this platform! Looking forward to connecting with everyone. 🎉',
                'privacy': 'friends',
                'like_count': 3,
                'comment_count': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created user1 post'))

        post3, created = Post.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'author': user2,
                'body': 'Just joined the platform! Still figuring things out but it looks great so far.',
                'privacy': 'public',
                'like_count': 2,
                'comment_count': 0
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created user2 post'))

        # Create comments
        self.stdout.write('\nCreating comments...')
        comment1, created = Comment.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'post': post1,
                'author': user1,
                'body': 'Thanks for creating this platform! Really enjoying the features.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created comment on admin post'))

        comment2, created = Comment.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'post': post1,
                'author': user2,
                'body': 'Great work! Looking forward to more updates.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created second comment on admin post'))

        # Create reactions
        self.stdout.write('\nCreating reactions...')
        reactions_data = [
            (user1, post1, 'love'),
            (user2, post1, 'like'),
            (admin, post2, 'like'),
            (user2, post2, 'wow'),
            (admin, post3, 'like'),
            (user1, post3, 'like'),
            (user2, comment1, 'like'),
        ]

        for reactor, target, reaction_type in reactions_data:
            target_type = 'post' if isinstance(target, Post) else 'comment'
            reaction, created = Reaction.objects.get_or_create(
                user=reactor,
                target_type=target_type,
                target_id=target.id,
                defaults={'type': reaction_type}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {reaction_type} reaction'))

        # Create groups
        self.stdout.write('\nCreating groups...')
        group1, created = Group.objects.get_or_create(
            slug='demo-tech-group',
            defaults={
                'name': 'Demo Tech Enthusiasts',
                'description': 'A group for tech enthusiasts to share and discuss the latest in technology.',
                'privacy': 'public',
                'owner': admin
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created tech group'))

        group2, created = Group.objects.get_or_create(
            slug='demo-social-group',
            defaults={
                'name': 'Demo Social Circle',
                'description': 'A private group for close friends to connect and share.',
                'privacy': 'private',
                'owner': user1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created social group'))

        # Add group members
        self.stdout.write('\nAdding group members...')
        group_members_data = [
            (group1, admin, 'admin'),
            (group1, user1, 'member'),
            (group1, user2, 'member'),
            (group2, user1, 'admin'),
            (group2, user2, 'member'),
        ]

        for group, member, role in group_members_data:
            membership, created = GroupMember.objects.get_or_create(
                group=group,
                user=member,
                defaults={'role': role, 'status': 'joined'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added {member.username} to {group.name}'))

        # Create pages
        self.stdout.write('\nCreating pages...')
        page1, created = Page.objects.get_or_create(
            slug='demo-tech-blog',
            defaults={
                'name': 'Demo Tech Blog',
                'category': 'Technology',
                'about': 'Sharing the latest tech news, tutorials, and insights.',
                'owner': admin,
                'follower_count': 150
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created tech blog page'))

        page2, created = Page.objects.get_or_create(
            slug='demo-photography',
            defaults={
                'name': 'Demo Photography',
                'category': 'Photography',
                'about': 'Capturing moments and sharing visual stories.',
                'owner': user1,
                'follower_count': 75
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created photography page'))

        # Create messages
        self.stdout.write('\nCreating messages...')
        thread_id1 = uuid.uuid4()
        message1, created = Message.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'thread_id': thread_id1,
                'sender': admin,
                'body': 'Hey! How are you enjoying the platform so far?'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created message from admin'))

        message2, created = Message.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'thread_id': thread_id1,
                'sender': user1,
                'body': 'It\'s great! Really love the interface and features.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created reply from user1'))

        thread_id2 = uuid.uuid4()
        message3, created = Message.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={
                'thread_id': thread_id2,
                'sender': user2,
                'body': 'Hi everyone! New here and excited to connect!'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created welcome message from user2'))

        # Create notifications
        self.stdout.write('\nCreating notifications...')
        notifications_data = [
            (user1, 'friend_request', 'friendship', friendship1.id),
            (admin, 'friend_request', 'friendship', friendship2.id),
            (admin, 'comment', 'comment', comment1.id),
            (admin, 'reaction', 'reaction', None),
            (user1, 'message', 'message', message1.id),
            (user2, 'group_invite', 'group', group1.id),
        ]

        for user, notif_type, ref_type, ref_id in notifications_data:
            notification, created = Notification.objects.get_or_create(
                user=user,
                type=notif_type,
                ref_type=ref_type,
                ref_id=ref_id,
                defaults={'is_read': False}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {notif_type} notification for {user.username}'))

        self.stdout.write(self.style.SUCCESS('\nFacebook demo data loaded successfully!'))

    def load_amazon_demo_data(self, admin, user1, user2):
        """Load Amazon-related demo data"""
        
        # Create categories
        self.stdout.write('\nCreating Amazon categories...')
        electronics, created = Category.objects.get_or_create(
            slug='electronics',
            defaults={'name': 'Electronics'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Electronics category'))

        books, created = Category.objects.get_or_create(
            slug='books',
            defaults={'name': 'Books'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Books category'))

        clothing, created = Category.objects.get_or_create(
            slug='clothing',
            defaults={'name': 'Clothing'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Clothing category'))

        # Create products
        self.stdout.write('\nCreating Amazon products...')
        products_data = [
            {
                'title': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'Premium noise-cancelling wireless headphones with 30-hour battery life.',
                'brand': 'TechSound',
                'price_cents': 19999,
                'category': electronics,
                'avg_rating': 4.5,
                'review_count': 128,
            },
            {
                'title': 'Smartphone Pro Max',
                'slug': 'smartphone-pro-max',
                'description': 'Latest flagship smartphone with advanced camera system and 5G connectivity.',
                'brand': 'TechCorp',
                'price_cents': 99999,
                'category': electronics,
                'avg_rating': 4.7,
                'review_count': 256,
            },
            {
                'title': 'Python Programming Guide',
                'slug': 'python-programming-guide',
                'description': 'Comprehensive guide to Python programming for beginners and advanced users.',
                'brand': 'TechBooks',
                'price_cents': 3499,
                'category': books,
                'avg_rating': 4.8,
                'review_count': 89,
            },
            {
                'title': 'Cotton T-Shirt Pack',
                'slug': 'cotton-t-shirt-pack',
                'description': 'Pack of 3 premium cotton t-shirts in assorted colors.',
                'brand': 'ComfortWear',
                'price_cents': 2999,
                'category': clothing,
                'avg_rating': 4.2,
                'review_count': 45,
            },
        ]

        created_products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults=product_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.title}'))
                # Generate SKU
                product.sku = f"SKU-{product.id.hex[:8].upper()}"
                product.save()
            created_products.append(product)

        # Create product images
        self.stdout.write('\nCreating product images...')
        for i, product in enumerate(created_products):
            ProductImage.objects.get_or_create(
                product=product,
                url=f'https://example.com/images/product_{i+1}_1.jpg',
                defaults={'is_primary': True}
            )
            ProductImage.objects.get_or_create(
                product=product,
                url=f'https://example.com/images/product_{i+1}_2.jpg',
                defaults={'is_primary': False}
            )
            self.stdout.write(self.style.SUCCESS(f'Added images for {product.title}'))

        # Create inventory
        self.stdout.write('\nCreating inventory...')
        for product in created_products:
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                defaults={
                    'quantity': 100,
                    'reserved': 5,
                    'warehouse': 'Main Warehouse'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created inventory for {product.title}'))

        # Create addresses
        self.stdout.write('\nCreating addresses...')
        addresses_data = [
            {
                'user': admin,
                'label': 'Home',
                'full_name': 'Admin User',
                'line1': '123 Main Street',
                'line2': 'Apt 4B',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA',
                'phone': '+1-555-0123',
                'is_default': True,
            },
            {
                'user': user1,
                'label': 'Work',
                'full_name': 'Test User 1',
                'line1': '456 Business Ave',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94102',
                'country': 'USA',
                'phone': '+1-555-0456',
                'is_default': True,
            },
            {
                'user': user2,
                'label': 'Home',
                'full_name': 'Test User 2',
                'line1': '789 Residential Blvd',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60601',
                'country': 'USA',
                'phone': '+1-555-0789',
                'is_default': True,
            },
        ]

        created_addresses = []
        for address_data in addresses_data:
            address, created = Address.objects.get_or_create(
                user=address_data['user'],
                label=address_data['label'],
                defaults=address_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created address for {address_data["user"].username}'))
            created_addresses.append(address)

        # Create carts and cart items
        self.stdout.write('\nCreating carts and cart items...')
        for user in [admin, user1, user2]:
            cart, created = Cart.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created cart for {user.username}'))

            # Add items to cart
            for i, product in enumerate(created_products[:2]):  # Add first 2 products to each cart
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={
                        'quantity': 1,
                        'price_cents': product.price_cents,
                        'currency': 'USD'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Added {product.title} to {user.username}\'s cart'))

        # Create wishlists and wishlist items
        self.stdout.write('\nCreating wishlists...')
        for user in [admin, user1]:
            wishlist, created = Wishlist.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created wishlist for {user.username}'))

            # Add items to wishlist
            for product in created_products[2:]:  # Add last 2 products to wishlist
                WishlistItem.objects.get_or_create(
                    wishlist=wishlist,
                    product=product
                )
                self.stdout.write(self.style.SUCCESS(f'Added {product.title} to {user.username}\'s wishlist'))

        # Create orders
        self.stdout.write('\nCreating orders...')
        orders_data = [
            {
                'user': admin,
                'address': created_addresses[0],
                'status': 'delivered',
                'items': [(created_products[0], 1), (created_products[2], 2)],
            },
            {
                'user': user1,
                'address': created_addresses[1],
                'status': 'shipped',
                'items': [(created_products[1], 1)],
            },
            {
                'user': user2,
                'address': created_addresses[2],
                'status': 'created',
                'items': [(created_products[3], 3)],
            },
        ]

        for order_data in orders_data:
            subtotal = sum(product.price_cents * quantity for product, quantity in order_data['items'])
            shipping = 999  # $9.99 shipping
            tax = int(subtotal * 0.08)  # 8% tax
            total = subtotal + shipping + tax

            order, created = Order.objects.get_or_create(
                user=order_data['user'],
                status=order_data['status'],
                defaults={
                    'address': order_data['address'],
                    'subtotal_cents': subtotal,
                    'shipping_cents': shipping,
                    'tax_cents': tax,
                    'total_cents': total,
                    'currency': 'USD',
                    'placed_at': timezone.now() if order_data['status'] != 'created' else None,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created order for {order_data["user"].username}'))

                # Create order items
                for product, quantity in order_data['items']:
                    OrderItem.objects.get_or_create(
                        order=order,
                        product=product,
                        defaults={
                            'title': product.title,
                            'price_cents': product.price_cents,
                            'quantity': quantity,
                            'currency': 'USD'
                        }
                    )

                # Create payment for non-created orders
                if order_data['status'] != 'created':
                    Payment.objects.get_or_create(
                        order=order,
                        defaults={
                            'provider': 'stripe',
                            'provider_ref': f'ch_{uuid.uuid4().hex[:16]}',
                            'status': 'captured',
                            'amount_cents': total,
                            'currency': 'USD'
                        }
                    )

        # Create reviews
        self.stdout.write('\nCreating reviews...')
        reviews_data = [
            {
                'product': created_products[0],
                'user': admin,
                'rating': 5,
                'title': 'Excellent headphones!',
                'body': 'Best headphones I\'ve ever owned. Great sound quality and battery life.',
            },
            {
                'product': created_products[0],
                'user': user1,
                'rating': 4,
                'title': 'Good value',
                'body': 'Really good headphones for the price. Comfortable to wear for long periods.',
            },
            {
                'product': created_products[1],
                'user': user1,
                'rating': 5,
                'title': 'Amazing phone!',
                'body': 'The camera is incredible and the battery lasts all day.',
            },
            {
                'product': created_products[2],
                'user': admin,
                'rating': 4,
                'title': 'Great learning resource',
                'body': 'Very comprehensive guide for Python programming.',
            },
        ]

        for review_data in reviews_data:
            review, created = Review.objects.get_or_create(
                product=review_data['product'],
                user=review_data['user'],
                defaults=review_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created review for {review_data["product"].title}'))

        # Create audit logs
        self.stdout.write('\nCreating audit logs...')
        audit_logs_data = [
            {
                'user': admin,
                'action': 'product_created',
                'target_type': 'product',
                'target_id': created_products[0].id,
                'meta': {'title': created_products[0].title},
            },
            {
                'user': user1,
                'action': 'order_placed',
                'target_type': 'order',
                'meta': {'status': 'shipped'},
            },
            {
                'user': user2,
                'action': 'cart_updated',
                'target_type': 'cart',
                'meta': {'items_added': 2},
            },
        ]

        for log_data in audit_logs_data:
            audit_log, created = AuditLog.objects.get_or_create(
                user=log_data['user'],
                action=log_data['action'],
                target_type=log_data['target_type'],
                defaults=log_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created audit log for {log_data["action"]}'))

        self.stdout.write(self.style.SUCCESS('\nAmazon demo data loaded successfully!'))

    def load_instagram_demo_data(self, admin, user1, user2):
        """Load Instagram-related demo data"""
        
        # Create follows
        self.stdout.write('\nCreating Instagram follows...')
        follows_data = [
            (user1, admin, 'accepted'),
            (user2, admin, 'accepted'),
            (admin, user1, 'accepted'),
            (user1, user2, 'accepted'),
        ]

        for follower, followee, status in follows_data:
            follow, created = Follow.objects.get_or_create(
                follower=follower,
                followee=followee,
                defaults={'status': status}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created follow: {follower.username} -> {followee.username}'))

        # Create tags
        self.stdout.write('\nCreating Instagram tags...')
        tags_data = ['nature', 'photography', 'travel', 'food', 'lifestyle', 'tech', 'art', 'fitness']
        created_tags = {}
        
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'usage_count': 0}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_name}'))
            created_tags[tag_name] = tag

        # Create media posts
        self.stdout.write('\nCreating Instagram media posts...')
        media_data = [
            {
                'owner': admin,
                'type': 'image',
                'caption': 'Beautiful sunset at the beach! 🌅 Nature never fails to amaze me. #nature #sunset #photography',
                'location': 'Santa Monica Beach',
                'like_count': 45,
                'comment_count': 8,
                'urls': {'thumbnail': 'https://example.com/ig/sunset_thumb.jpg', 'full': 'https://example.com/ig/sunset_full.jpg'},
                'tags': ['nature', 'photography'],
            },
            {
                'owner': user1,
                'type': 'image',
                'caption': 'New tech setup! Loving the clean minimal workspace. 🖥️✨ #tech #workspace #setup',
                'location': 'Home Office',
                'like_count': 23,
                'comment_count': 3,
                'urls': {'thumbnail': 'https://example.com/ig/workspace_thumb.jpg', 'full': 'https://example.com/ig/workspace_full.jpg'},
                'tags': ['tech', 'lifestyle'],
            },
            {
                'owner': user2,
                'type': 'carousel',
                'caption': 'Food adventure! Tried this amazing new restaurant today. 🍕🍔 #food #restaurant #foodie',
                'location': 'Downtown Bistro',
                'like_count': 31,
                'comment_count': 5,
                'urls': {
                    'thumbnail': 'https://example.com/ig/food1_thumb.jpg',
                    'full': 'https://example.com/ig/food1_full.jpg',
                    'thumbnail_2': 'https://example.com/ig/food2_thumb.jpg',
                    'full_2': 'https://example.com/ig/food2_full.jpg'
                },
                'tags': ['food'],
            },
            {
                'owner': admin,
                'type': 'video',
                'caption': 'Morning workout complete! 💪 Feeling energized and ready to conquer the day. #fitness #workout #health',
                'location': 'Gym',
                'like_count': 18,
                'comment_count': 2,
                'urls': {'thumbnail': 'https://example.com/ig/workout_thumb.jpg', 'video': 'https://example.com/ig/workout.mp4'},
                'tags': ['fitness'],
            },
        ]

        created_media = []
        for media_item in media_data:
            media, created = Media.objects.get_or_create(
                id=uuid.uuid4(),
                defaults={
                    'owner': media_item['owner'],
                    'type': media_item['type'],
                    'urls': media_item['urls'],
                    'caption': media_item['caption'],
                    'location': media_item['location'],
                    'like_count': media_item['like_count'],
                    'comment_count': media_item['comment_count'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created media post for {media_item["owner"].username}'))
                
                # Add tags to media
                for tag_name in media_item['tags']:
                    if tag_name in created_tags:
                        MediaTag.objects.get_or_create(media=media, tag=created_tags[tag_name])
                        # Update tag usage count
                        tag = created_tags[tag_name]
                        tag.usage_count += 1
                        tag.save()
                        
            created_media.append(media)

        # Create stories
        self.stdout.write('\nCreating Instagram stories...')
        stories_data = [
            {
                'owner': user1,
                'media_url': 'https://example.com/ig/story1.jpg',
                'expires_at': timezone.now() + timezone.timedelta(hours=24),
                'view_count': 15,
            },
            {
                'owner': user2,
                'media_url': 'https://example.com/ig/story2.jpg',
                'expires_at': timezone.now() + timezone.timedelta(hours=20),
                'view_count': 12,
            },
            {
                'owner': admin,
                'media_url': 'https://example.com/ig/story3.jpg',
                'expires_at': timezone.now() + timezone.timedelta(hours=18),
                'view_count': 28,
            },
        ]

        for story_data in stories_data:
            story, created = Story.objects.get_or_create(
                id=uuid.uuid4(),
                defaults=story_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created story for {story_data["owner"].username}'))

        # Create comments
        self.stdout.write('\nCreating Instagram comments...')
        comments_data = [
            {
                'media': created_media[0],
                'user': user1,
                'body': 'Absolutely stunning! 😍 Love the colors in this sunset.',
            },
            {
                'media': created_media[0],
                'user': user2,
                'body': 'Perfect timing! Where was this taken?',
            },
            {
                'media': created_media[1],
                'user': admin,
                'body': 'Clean setup! What monitor are you using?',
            },
            {
                'media': created_media[2],
                'user': admin,
                'body': 'That looks delicious! 😋',
            },
            {
                'media': created_media[0],
                'user': admin,
                'body': 'Thanks! It was at Santa Monica Beach.',
                'parent': None,  # This will be set after creating the first comment
            },
        ]

        created_comments = []
        for i, comment_data in enumerate(comments_data):
            # For the last comment, set it as a reply to the first comment
            if i == 4:
                comment_data['parent'] = created_comments[0]
            
            comment, created = IGComment.objects.get_or_create(
                id=uuid.uuid4(),
                defaults=comment_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created comment by {comment_data["user"].username}'))
            created_comments.append(comment)

        # Create likes
        self.stdout.write('\nCreating Instagram likes...')
        likes_data = [
            (user1, created_media[0]),
            (user2, created_media[0]),
            (admin, created_media[1]),
            (user2, created_media[1]),
            (admin, created_media[2]),
            (user1, created_media[2]),
            (user1, created_media[3]),
        ]

        for liker, media_item in likes_data:
            like, created = Like.objects.get_or_create(
                user=liker,
                media=media_item
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created like by {liker.username}'))

        # Create direct message threads
        self.stdout.write('\nCreating Instagram direct messages...')
        # Thread between admin and user1
        thread1, created = DirectThread.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={'is_group': False}
        )
        if created:
            DirectParticipant.objects.create(thread=thread1, user=admin, role='admin')
            DirectParticipant.objects.create(thread=thread1, user=user1, role='member')
            self.stdout.write(self.style.SUCCESS('Created DM thread: admin <-> user1'))

        # Thread between all users (group chat)
        thread2, created = DirectThread.objects.get_or_create(
            id=uuid.uuid4(),
            defaults={'is_group': True}
        )
        if created:
            DirectParticipant.objects.create(thread=thread2, user=admin, role='admin')
            DirectParticipant.objects.create(thread=thread2, user=user1, role='member')
            DirectParticipant.objects.create(thread=thread2, user=user2, role='member')
            self.stdout.write(self.style.SUCCESS('Created group DM thread: admin, user1, user2'))

        # Create direct messages
        messages_data = [
            {
                'thread': thread1,
                'sender': admin,
                'body': 'Hey! Love your recent post about the workspace setup!',
            },
            {
                'thread': thread1,
                'sender': user1,
                'body': 'Thanks! Let me know if you want any setup tips 😊',
            },
            {
                'thread': thread2,
                'sender': user2,
                'body': 'Hey everyone! Who wants to grab coffee this weekend? ☕',
            },
            {
                'thread': thread2,
                'sender': admin,
                'body': 'Count me in! Saturday works for me.',
            },
            {
                'thread': thread2,
                'sender': user1,
                'body': 'Sounds great! Saturday afternoon?',
            },
        ]

        for message_data in messages_data:
            message, created = DirectMessage.objects.get_or_create(
                id=uuid.uuid4(),
                defaults=message_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created DM from {message_data["sender"].username}'))

        # Create notifications
        self.stdout.write('\nCreating Instagram notifications...')
        notifications_data = [
            (user1, 'like', 'media', created_media[0].id),
            (user2, 'like', 'media', created_media[0].id),
            (admin, 'comment', 'comment', created_comments[0].id),
            (admin, 'follow', 'follow', None),
            (user1, 'follow', 'follow', None),
            (user2, 'dm', 'dm', None),
            (admin, 'mention', 'media', created_media[1].id),
        ]

        for user, notif_type, ref_type, ref_id in notifications_data:
            notification, created = IGNotification.objects.get_or_create(
                user=user,
                type=notif_type,
                ref_type=ref_type,
                ref_id=ref_id,
                defaults={'is_read': False}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created {notif_type} notification for {user.username}'))

        self.stdout.write(self.style.SUCCESS('\nInstagram demo data loaded successfully!'))