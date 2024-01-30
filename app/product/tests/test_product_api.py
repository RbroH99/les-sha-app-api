"""
Tests for product API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Product,
    Product_type,
    Rating,
    Tag,
    Resource
)

from product.serializers import (
    ProductSerializer,
    ProductDetailSerializer,
)


PRODUCTS_URL = reverse('product:product-list')


def detail_url(product_id):
    """Create and return a product detail URL."""
    return reverse('product:product-detail', args=[product_id])


def create_product(**params):
    """Create and return a sample product."""
    defaults = {
        'name': 'Sample product name',
        'price': Decimal('350'),
        'description': 'Sample description'
    }
    defaults.update(params)

    product = Product.objects.create(**defaults)
    return product


def create_staff_client(email):
    """Create and return superuser and staff_client."""
    staff_client = APIClient()
    superuser = get_user_model().objects.create_superuser(
            email=email,
            password='pass123',
        )
    staff_client.force_authenticate(superuser)

    return (superuser, staff_client)


class PublicProductAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.superuser, self.staff_client \
            = create_staff_client('superuser1@example.com')

    def test_retrieve_products(self):
        """Test retrieving the products."""
        create_product(name='Product1')
        create_product(name='Product2')

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_product_error(self):
        """Test unauthenticated users can't create products."""
        res = self.client.post(PRODUCTS_URL, {
            'name': 'Test Product',
            'price': Decimal('350'),
            'description': 'Test Description'
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_product_rating_succesfull(self):
        """Test the average rating of a product is returned on detail."""
        product = Product.objects.create(name='Test Product',
                                         price=Decimal('300'))
        user1 = get_user_model().objects.create_user(email='user1@example.com',
                                                     password='Tetspass123')
        user2 = get_user_model().objects.create_user(email='user2@example.com',
                                                     password='Tetspass123')
        Rating.objects.create(user=user1, product=product, value=2)
        Rating.objects.create(user=user2, product=product, value=5)

        url = detail_url(product.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['rating'], ((5+2)/2))


class PrivateProductsAPITests(TestCase):
    """Test authenticathed API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)
        self.superuser, self.staff_client \
            = create_staff_client('superuser2@example.com')

    # ####_NON-STAFF USERS TESTS_#### #

    def test_non_staff_create_product(self):
        """Test a non-staff client can't create a product."""
        res = self.client.post(PRODUCTS_URL, {
            'name': 'Test Product',
            'price': Decimal('350'),
            'description': 'Test Description'
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_product_detail(self):
        """Test create Product detail."""
        product = create_product(name='Test Product')

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(res.data, serializer.data)

    def test_non_staff_update_product(self):
        """Test non-staff users can't update a product."""
        product = create_product(name='Test Product')

        url = detail_url(product.id)

        # full update
        res = self.client.put(url, {'name': 'New Name'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # partial update
        res = self.client.patch(url, {'name': 'New Name'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_delete_product_error(self):
        """Test non-staff users attempt delete product returns error."""
        product = create_product(name='Test Name')

        url = detail_url(product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ####_STAFF USERS TESTS_#### #

    def test_staff_create_product(self):
        """Test staff can create product."""
        payload = {
            'name': 'Test Product',
            'price': Decimal('350'),
            'description': 'Test Description'
        }
        res = self.staff_client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)

    def test_staff_partial_update_product(self):
        """Test a staff user can make partial update product."""
        product = create_product(
            name='Test Name',
            price=Decimal('200'),
            description='Test product description.'
        )
        payload = {
            'name': 'Test Product'
        }

        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        updated_product = Product.objects.get(id=res.data['id'])
        self.assertEqual(updated_product.name, payload['name'])
        self.assertEqual(updated_product.price, product.price)
        self.assertEqual(updated_product.description, product.description)

    def test_staff_full_update_product(self):
        """Test a staff user can make partial update product."""
        product = create_product(
            name='Test Name',
            price=Decimal('200'),
            description='Test product description.'
        )
        payload = {
            'name': 'Test Product',
            'price': Decimal('350'),
            'description': 'New test Description'
        }

        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product = Product.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)

    def test_staff_delete_product(self):
        """Test staff delete a product is successful."""
        product = create_product(name='Test Name')

        url = detail_url(product.id)
        res = self.staff_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        res = self.staff_client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_type_on_update(self):
        """Test creating a new product type on product update."""
        product = create_product(name='Product Name')

        payload = {'types': [{'name': 'Bracelet'}]}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        types_list = []
        for types in product.types.all():
            types_list.append(types.name)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('Bracelet', types_list)

    def test_update_assign_type(self):
        """Test assigning an existing type when updating a new product."""
        type_bracelet = Product_type.objects.create(name='Bracelet')
        product = create_product(name='Test product')
        product.types.add(type_bracelet)

        type_necklace = Product_type.objects.create(name='Necklace')
        payload = {"types": [{"name": "Necklace"}]}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(type_necklace, product.types.all())

    def test_clear_product_types(self):
        """Test clearing a product types."""
        type = Product_type.objects.create(name='Test Type')
        product = create_product(name='Test Product')
        product.types.add(type)

        payload = {'types': []}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.types.count(), 0)

    def test_create_tag_on_update(self):
        """Test creating a new tag on product update."""
        product = create_product(name='Product Name')

        payload = {"tags": [{"name": "Bracelet"}]}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        tags_list = []
        for tag in product.tags.all():
            tags_list.append(tag.name)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('Bracelet', tags_list)

    def test_update_assign_tag(self):
        """Test assigning an existing tag when updating a product."""
        tag_fimo = Tag.objects.create(name='Fimo')
        product = create_product(name='Test product')
        product.tags.add(tag_fimo)

        tag_rose = Tag.objects.create(name='Rose')
        payload = {"tags": [{"name": "Rose"}]}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_rose, product.tags.all())

    def test_clear_product_tags(self):
        """Test clearing a product tags."""
        tag = Tag.objects.create(name='Test Tag')
        product = create_product(name='Test Product')
        product.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(product.id)
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(product.tags.count(), 0)

    def test_update_assign_resources(self):
        """Test updating resources."""
        product = create_product(name='Test Product')
        resource1 = Resource.objects.create(name='Set')
        product.resources.add(resource1)
        resource2 = Resource.objects.create(name='Playa')

        url = detail_url(product.id)
        res = self.staff_client.patch(url, {"resources": [resource2.id]}, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertIn(resource2, product.resources.all())

    def test_clear_resources(self):
        """Test clearing resources of a product."""
        resource1 = Resource.objects.create(name='Set')
        resource2 = Resource.objects.create(name='Forest')
        product = create_product(name='Product')
        product.resources.set([resource1.id, resource2.id])

        url = detail_url(product.id)
        res = self.staff_client.patch(url, {"resources": []}, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['resources'], [])
