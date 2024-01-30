"""
Tests for the resource API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Resource

from product.serializers import ResourceSerializer

from decimal import Decimal


RESOURCES_URL = reverse('product:resource-list')


def detail_url(resource_id):
    """Return detail url of a resource."""
    return reverse('product:resource-detail', args=[resource_id])


def create_user(email='user@exampel.com', password='testpass123'):
    """Create and return new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_staff_client(email):
    """Create and return superuser and staff_client."""
    staff_client = APIClient()
    superuser = get_user_model().objects.create_superuser(
            email=email,
            password='pass123',
        )
    staff_client.force_authenticate(superuser)

    return (superuser, staff_client)


class PublicResourceAPITest(TestCase):
    """Test for the unauthenticated request to Resources API."""

    def setUp(self):
        self.client = APIClient()

    def test_resources_list(self):
        """Test listing resources."""
        Resource.objects.create(name='Fimo')
        Resource.objects.create(name='Pearl')

        res = self.client.get(RESOURCES_URL)

        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_resource_create_error(self):
        """Test unauthenticated user create resources results in error."""
        res = self.client.post(RESOURCES_URL, {"name": "Test Name"}, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Resource.objects.all().count(), 0)

    def test_resource_update_error(self):
        """Test unauthenticated user can't update resources."""
        resource = Resource.objects.create(name='Test Name',
                                           price=Decimal('10'))

        url = detail_url(resource.id)
        payload = {
            "name": "New Name",
            "price": Decimal('15')
        }
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        resource.refresh_from_db()
        self.assertNotEqual(resource.name, payload['name'])
        self.assertNotEqual(resource.price, payload['price'])

    def test_reource_delete_error(self):
        """Test unauthenticated can't delete resources."""
        resource = Resource.objects.create(name='Test Name')

        url = detail_url(resource.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Resource.objects.all().count(), 1)


class PrivateResourceAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='user@example.com',
                                                         password='Testpass123')
        self.client.force_authenticate(self.user)
        self.superuser, self.staff_client \
            = create_staff_client('superuser1@example.com')

    # ***_NON-STAFF USERS TESTS_*** #

    def test_non_staff_create_resource(self):
        """Test non-staff can't create resources."""
        payload = {
            "name": "Test Name",
            "price": Decimal('15')
        }
        res = self.client.post(RESOURCES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.all().count(), 0)

    def test_non_staff_update_resource(self):
        """Test non-staff can't update resource."""
        resource = Resource.objects.create(name='Test Name')

        url = detail_url(resource.id)
        payload = {"name": "New name"}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        resource.refresh_from_db()
        self.assertNotEqual(resource.name, payload['name'])

    def test_non_staff_delete_resource(self):
        """Test non-staff can't delete resource from database."""
        resource = Resource.objects.create(name="Test Name")

        url = detail_url(resource.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Resource.objects.all().count(), 1)

    # ***_STAFF USERS TESTS_*** #

    def test_staff_create_resource(self):
        """Test staff user create resource."""
        payload = {
            "name": "Test Resource",
            "price": Decimal('5')
        }
        res = self.staff_client.post(RESOURCES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.all().count(), 1)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(Decimal(res.data['price']), payload['price'])

    def test_staff_update_resource(self):
        """Test staff user can update a resource."""
        resource = Resource.objects.create(name='Test Resource', price=Decimal('3'))
        url = detail_url(resource.id)

        # Full Update
        payload = {
            "name": "New Resource",
            "price": Decimal('5')
        }
        res = self.staff_client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        resource.refresh_from_db()
        self.assertEqual(resource.name, payload['name'])
        self.assertEqual(resource.price, payload['price'])

        # Partial Update
        payload = {"price": Decimal('4')}
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        resource.refresh_from_db()
        self.assertEqual(resource.price, payload['price'])

    def test_staff_delete_resource(self):
        """Test staff user delete resource."""
        resource = Resource.objects.create(name='Test Name')

        url = detail_url(resource.id)
        res = self.staff_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Resource.objects.all().count(), 0)
