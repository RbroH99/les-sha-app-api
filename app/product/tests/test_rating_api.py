"""
Test for the product ratings API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Rating,
    Product,
)

from product.serializers import RatingSerializer

from decimal import Decimal


RATING_URL = reverse('product:rating-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(rating_id):
    """Create and return a rating detail URL."""
    return reverse('product:rating-detail', kwargs={'pk': rating_id})


def create_staff_client(email):
    """Create and return superuser and staff_client."""
    staff_client = APIClient()
    superuser = get_user_model().objects.create_superuser(
            email=email,
            password='pass123',
        )
    staff_client.force_authenticate(superuser)

    return (superuser, staff_client)


class PublicRatingTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.superuser, self.staff_client \
            = create_staff_client('superuser1@example.com')

    def test_retrieve_ratings(self):
        """Test retrieving ratings."""
        product = Product.objects.create(name='Test Product',
                                         price=Decimal('200'))
        user1 = create_user(email='user1@example.com')
        user2 = create_user(email='user2@example.com')
        Rating.objects.create(user=user1, product=product, value=3)
        Rating.objects.create(user=user2, product=product, value=4)

        res = self.client.get(RATING_URL)

        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_unauthenticated_rate_fail(self):
        """Test unauthenticated users can't rate products."""
        product = Product.objects.create(name='Test Product',
                                         price=Decimal('200'))
        user = create_user(email='user@example.com')

        res = self.client.post(RATING_URL, user=user, product=product, value=5)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRatingTests(TestCase):
    """Test for authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)
        self.superuser, self.staff_client \
            = create_staff_client('superuser2@example.com')

    def test_create_unique_rating(self):
        """Test combination user-product is unique for rating."""
        product = Product.objects.create(name='Test Product',
                                         price=Decimal('200'))
        user = create_user(email='user@example.com')
        Rating.objects.create(user=user, product=product, value=3)

        res = self.client.post(RATING_URL, user=user, product=product, value=5)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(res.data['value'], 5)

    def test_update_rating(self):
        """Test updating a rating is successful."""
        product = Product.objects.create(name='Test Product',
                                         price=Decimal('200'))
        user = create_user(email='user@example.com')
        rating = Rating.objects.create(user=user, product=product, value=1)

        payload = {"value": 4}
        url = detail_url(rating.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['value'], payload['value'])
