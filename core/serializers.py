from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer
from .models import User
import uuid


class UserCreateSerializer(DjoserUserCreateSerializer):
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ('id', 'email', 'password', 'full_name', 'username')

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        if not username:
            email = validated_data.get('email')
            base_username = email.split('@')[0] if email else 'user'
            unique_id = str(uuid.uuid4())[:8]
            username = f"{base_username}_{unique_id}"
        validated_data['username'] = username
        return super().create(validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'bio', 'username')


class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = ('id', 'email', 'full_name', 'created_at')
