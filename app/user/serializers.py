"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers

import re


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'phone']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5},
                        'phone': {
                            'required': False,
                            'allow_null': True,
                            'allow_blank': True,
                                }
                        }

    def validate_phone(self, phone):
        """Validates the phone number."""
        pattern = re.compile(r"(\+\d{1,3})?\s?\(?\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{3}")
        if not pattern.match(phone):
            msg = _("Invalid phone number.")
            raise serializers.ValidationError(msg)

        return phone

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authnticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
