"""
URL mapping for the product app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from product import views


router = DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('product_types', views.Product_typeViewSet)
router.register('ratings', views.RatingViewSet)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
]
