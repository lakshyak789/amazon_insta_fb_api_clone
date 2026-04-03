from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

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

        self.stdout.write(self.style.SUCCESS('\nDemo data loaded successfully!'))