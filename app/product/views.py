"""
Views for the Product API.
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from core.models import (
    Product,
    Product_type,
    Rating,
    Tag,
    Resource,
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
        elif self.action == 'upload_image':
            return serializers.ProductImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to product."""
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class TagViewSet(viewsets.ModelViewSet):
    """Manage Tags in database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [DenyPostPermission]


class ResourceViewSet(viewsets.ModelViewSet):
    """Manage resources in database."""
    serializer_class = serializers.ResourceSerializer
    queryset = Resource.objects.all()
    permission_classes = [DenyPostPermission]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'upload_image':
            return serializers.ResourceImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to recipe."""
        resource = self.get_object()
        serializer = self.get_serializer(resource, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
