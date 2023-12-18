"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model

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
            raise serializers.ValidationError("Invalid phone number.")

        return phone

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
