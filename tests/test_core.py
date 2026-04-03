import pytest
from django.contrib.auth import get_user_model
from core.pagination import StandardResultsSetPagination
from core.errors import APIException

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email='modeltest@example.com',
            password='ModelTest123!',
            full_name='Model Test'
        )
        assert user.email == 'modeltest@example.com'
        assert user.full_name == 'Model Test'
        assert user.check_password('ModelTest123!')

    def test_create_user_without_email_fails(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='Pass123!')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='Super123!',
            full_name='Super User'
        )
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    def test_user_uuid_primary_key(self):
        user = User.objects.create_user(
            email='uuid@example.com',
            password='Uuid123!'
        )
        assert user.id is not None


@pytest.mark.django_db
class TestPagination:
    def test_pagination_default_page_size(self):
        pagination = StandardResultsSetPagination()
        assert pagination.page_size == 20
        assert pagination.page_size_query_param == 'limit'
        assert pagination.max_page_size == 100


@pytest.mark.django_db
class TestAPIException:
    def test_api_exception_creation(self):
        exc = APIException('TEST_ERROR', 'Test message', status_code=400)
        assert exc.code == 'TEST_ERROR'
        assert exc.message == 'Test message'
        assert exc.status_code == 400

    def test_api_exception_with_details(self):
        exc = APIException(
            'VALIDATION_ERROR',
            'Invalid input',
            details=[{'field': 'email', 'msg': 'required'}],
            status_code=422
        )
        assert len(exc.details) == 1
        assert exc.details[0]['field'] == 'email'
