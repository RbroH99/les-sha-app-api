"""
Serializers for Products API.
"""
from rest_framework import serializers

from core.models import (
    Product,
    Product_type
)


class Product_typeSerializer(serializers.ModelSerializer):
    """Serializer for product types."""

    class Meta:
        model = Product_type
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ['id',
                  'name',
                  'price']
        read_only_fields = ['id']


class ProductDetailSerializer(ProductSerializer):
    """Serializer for recipe detail view."""
    types = Product_typeSerializer(many=True, read_only=True)

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description', 'types']
