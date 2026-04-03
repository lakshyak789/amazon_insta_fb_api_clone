from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

from .serializers import UserSerializer

User = get_user_model()


def get_tokens_for_user(user, role=None):
    """Generate JWT tokens with role claim"""
    refresh = RefreshToken.for_user(user)
    
    if role is None:
        role = 'admin' if user.is_staff else getattr(user, 'role', 'customer')
    
    access_token = AccessToken()
    access_token['user_id'] = str(user.id)
    access_token['email'] = user.email
    access_token['role'] = role
    access_token['is_staff'] = user.is_staff
    
    refresh['user_id'] = str(user.id)
    refresh['role'] = role
    refresh['is_staff'] = user.is_staff
    
    return {
        'token': str(access_token),
        'refresh': str(refresh)
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        username = request.data.get('username', email.split('@')[0])
        full_name = request.data.get('fullName', '')

        if not email or not password:
            return Response(
                {'error': {'code': 'VALIDATION_ERROR', 'message': 'Email and password required', 'details': []}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'error': {'code': 'VALIDATION_ERROR', 'message': 'Email already exists', 'details': [{'field': 'email', 'msg': 'taken'}]}},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=email,
            password=password,
            username=username,
            full_name=full_name
        )

        tokens = get_tokens_for_user(user, role='customer')

        return Response({
            'token': tokens['token'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': {'code': 'VALIDATION_ERROR', 'message': 'Email and password required', 'details': []}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid credentials', 'details': []}},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid credentials', 'details': []}},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': {'code': 'ACCOUNT_DISABLED', 'message': 'Account is disabled', 'details': []}},
                status=status.HTTP_401_UNAUTHORIZED
            )

        role = 'admin' if user.is_staff else getattr(user, 'role', 'customer')
        tokens = get_tokens_for_user(user, role=role)

        return Response({
            'token': tokens['token'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refreshToken')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refreshToken')
        if not refresh_token:
            return Response(
                {'error': {'code': 'VALIDATION_ERROR', 'message': 'Refresh token required', 'details': []}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.get('user_id')
            role = refresh.get('role', 'customer')
            is_staff = refresh.get('is_staff', False)
            
            access_token = AccessToken()
            access_token['user_id'] = user_id
            access_token['role'] = role
            access_token['is_staff'] = is_staff
            
            if role == 'admin' or is_staff:
                try:
                    user = User.objects.get(id=user_id)
                    access_token['email'] = user.email
                except User.DoesNotExist:
                    pass
            
            return Response({
                'token': str(access_token)
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token', 'details': []}},
                status=status.HTTP_401_UNAUTHORIZED
            )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            {'error': {'code': 'VALIDATION_ERROR', 'message': 'Invalid input', 'details': serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST
        )