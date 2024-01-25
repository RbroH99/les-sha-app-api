"""
Serializers for Products API.
"""
from rest_framework import serializers

from core.models import (
    Product,
    Product_type,
    Rating
)


class Product_typeSerializer(serializers.ModelSerializer):
    """Serializer for product types."""

    class Meta:
        model = Product_type
        fields = ['id', 'name']
        read_only_fields = ['id']


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""

    class Meta:
        model = Rating
        fields = ['id', 'user', 'product', 'value']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    types = Product_typeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id',
                  'name',
                  'price',
                  'types']
        read_only_fields = ['id']
        extra_kwargs = {'types': {'required': False,
                                  'allow_null': True,
                                  'allow_blank': True,
                                  }
                        }

    def _get_or_create_types(self, types, product):
        """Handle getting or creating types as needed."""
        for type in types:
            type_obj, created = Product_type.objects.get_or_create(**type)
            product.types.add(type_obj)

    def create(self, validated_data):
        """Create product."""
        types = validated_data.pop('types', None)
        product = Product.objects.create(**validated_data)

        if types is not None:
            self._get_or_create_types(types, product)

        return product

    def update(self, instance, validated_data):
        """Update product."""
        types = validated_data.pop('types', None)
        if types is not None:
            instance.types.clear()
            self._get_or_create_types(types, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProductDetailSerializer(ProductSerializer):
    """Serializer for recipe detail view."""
    rating = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['description', 'rating']

    def get_rating(self, obj):
        return obj.rating
