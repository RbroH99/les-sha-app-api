"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Tests email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_product(self):
        """Test creating a product is succesful."""
        product = models.Product.objects.create(
            name='Sample product name',
            price=Decimal('350'),
            description='Saple description',
        )

        self.assertEqual(str(product), product.name)

    def test_create_product_type(self):
        """Test creating a product type is successful."""
        product_type = models.Product_type.objects.create(name='Type1')

        self.assertEqual(str(product_type), product_type.name)

    def test_create_rating(self):
        """Test creating a rating is successfull."""
        user = create_user()
        product = models.Product.objects.create(name='Test Product',
                                                price=Decimal('350'))
        rating = models.Rating.objects.create(user=user, product=product, value=3)

        self.assertEqual(str(rating), f'{product.name}>{user.name}>{rating.value}')

    def test_create_tag(self):
        """Test creating a tag is successful."""
        tag = models.Tag.objects.create(name='Playa')

        self.assertEqual(str(tag), 'Playa')

    def test_create_resource(self):
        """Test creating a resource is successful."""
        resource = models.Resource.objects.create(name="Fimo")

        self.assertEqual(str(resource), resource.name)
