"""
Test for the product types API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product_type

from product.serializers import Product_typeSerializer


PRODUCT_TYPES_URL = reverse('product:product_type-list')


def detail_url(type_id):
    """Create and return a product type detail URL."""
    return reverse('product:product_type-detail', kwargs={'pk': type_id})


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email, password)


def create_staff_client(email):
    """Create and return superuser and staff_client."""
    staff_client = APIClient()
    superuser = get_user_model().objects.create_superuser(
            email=email,
            password='pass123',
        )
    staff_client.force_authenticate(superuser)

    return (superuser, staff_client)


class PublicProduct_typesApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUP(self):
        self.client = APIClient()
        self.superuser, self.staff_client \
            = create_staff_client('superuser1@example.com')

    def test_retrieve_product_types(self):
        """Test retrieving a list of product types."""
        Product_type.objects.create(name='Necklace')
        Product_type.objects.create(name='Bracelet')

        res = self.client.get(PRODUCT_TYPES_URL)

        product_types = Product_type.objects.all().order_by('-name')
        serializer = Product_typeSerializer(product_types, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_unauthenticated_create_product_type_error(self):
        """Test unauthenticated users cany create product types."""
        res = self.client.post(PRODUCT_TYPES_URL, {'name': 'Bracelet'})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProduct_typesApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.superuser, self.staff_client \
            = create_staff_client('superuser2@example.com')

    # ####_NON-STAFF USERS TESTS_#### #

    def test_non_staff_create_product_type(self):
        """Test non-staff users can't create product types."""
        res = self.client.post(PRODUCT_TYPES_URL, {'name': 'Product type'})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product_type.objects.all().count(), 0)

    def test_get_product_type_detail(self):
        """"Test retrieving a product type detail."""
        type = Product_type.objects.create(name='Test Type')

        url = detail_url(type.id)
        res = self.client.get(url)

        serializer = Product_typeSerializer(type)
        self.assertEqual(res.data, serializer.data)

    def test_non_staff_update_product_type(self):
        """Test non-staff users can't update product types."""
        type = Product_type.objects.create(name='Test Type')

        url = detail_url(type)
        res = self.client.put(url, {'name': 'New Type'}, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_delete_product_type_error(self):
        """Tests a non-staff user deleting type results in error."""
        type = Product_type.objects.create(name='Test Type')

        url = detail_url(type.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product_type.objects.all().count(), 1)

    # ####_STAFF USERS TESTS_#### #

    def test_staff_create_product_type(self):
        """Test staff user create product type successful."""
        res = self.staff_client.post(PRODUCT_TYPES_URL, {'name': 'Type'})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], 'Type')

    def test_staff_update_product_type(self):
        """Test a staff user update product type successful."""
        type = Product_type.objects.create(name='Test Type')
        payload = {'name': 'New Type'}

        url = detail_url(type.id)
        res = self.staff_client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], payload['name'])

    def test_staff_delete_product_type(self):
        """Test a staff user can delete product types from db."""
        type = Product_type.objects.create(name='Test Product type')

        url = detail_url(type.id)
        res = self.staff_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(type, Product_type.objects.all())
