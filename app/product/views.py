"""
Views for the Product API.
"""
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import (
    viewsets,
    mixins,
)

from core.models import (
    Product,
    Product_type,
    Rating,
)
from product import serializers

from .permissions import DenyPostPermission


class ProductViewSet(viewsets.ModelViewSet):
    """View for manage the product APIs."""
    serializer_class = serializers.ProductDetailSerializer
    queryset = Product.objects.all()
    permission_classes = [DenyPostPermission]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ProductSerializer

        return self.serializer_class


class Product_typeViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """Manage product types in the database."""
    serializer_class = serializers.Product_typeSerializer
    queryset = Product_type.objects.all()
    permission_classes = [DenyPostPermission]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class RatingViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """Manage Ratings in the database."""
    serializer_class = serializers.RatingSerializer
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
