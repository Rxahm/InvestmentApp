# backend/app/accounts/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'two_factor_secret')
        extra_kwargs = {'two_factor_secret': {'write_only': True}}
