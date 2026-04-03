import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        email='testuser@example.com',
        password='TestPass123!',
        full_name='Test User',
        username='testuser'
    )
    return user


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        email='admin@example.com',
        password='AdminPass123!',
        full_name='Admin User',
        is_staff=True,
        role='admin',
        username='admin'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = admin_user
    return api_client


@pytest.fixture
def another_user(db):
    user = User.objects.create_user(
        email='another@example.com',
        password='AnotherPass123!',
        full_name='Another User',
        username='another'
    )
    return user


@pytest.fixture
def authenticated_client_2(api_client, another_user):
    refresh = RefreshToken.for_user(another_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = another_user
    return api_client
