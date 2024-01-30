"""
Test for tag API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
)

from product.serializers import TagSerializer

TAGS_URL = reverse('product:tag-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse('product:tag-detail', kwargs={'pk': tag_id})


def create_staff_client(email):
    """Create and return superuser and staff_client."""
    staff_client = APIClient()
    superuser = get_user_model().objects.create_superuser(
            email=email,
            password='pass123',
        )
    staff_client.force_authenticate(superuser)

    return (superuser, staff_client)


class PublicTagAPITest(TestCase):
    """Tests for the public Tag API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_tags(self):
        """Test retrieving tags list."""
        Tag.objects.create(name='Playa')
        Tag.objects.create(name='Conjunto')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_tag_fail(self):
        """Test unauthenticated users can't create tags."""
        payload = {"name": "Test Tag"}

        res = self.client.post(TAGS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(payload['name'], res.data)

    def test_update_fail(self):
        """Test unauthenticated users updating tags fails."""
        tag = Tag.objects.create(name='Tag Name')

        payload = {"name": "New Name"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload, format='json')

        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(tag.name, payload['name'])


class PrivateTagAPITests(TestCase):
    """Tests for the authenticated requests to the tags API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com')
        self.client.force_authenticate(self.user)
        superuser, staff_client = \
            create_staff_client('superuser@example.com')

    # ***_NON-STAFF USERS TESTS_*** #

    def test_non_staff_create_tag_fail(self):
        """Test non-staf users creating tags results in error."""
        res = self.client.post(TAGS_URL, {"name": "Test Tag"})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_update_tag_fail(self):
        """Test non-staff users updating tags results in error."""
        tag = Tag.objects.create(name='Test Name')

        url = detail_url(tag.id)
        payload = {"name": "New Name"}
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        tag.refresh_from_db()
        self.assertNotEqual(payload['name'], tag.name)

    def test_non_staff_list_tags_success(self):
        """Test non-staff authenticathed user get tag lists success."""
        Tag.objects.create(name='Set')
        Tag.objects.create(name='Azul')

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_non_staff_delete_tag_error(self):
        """Test non-staff authenticated users deleting tag results in error."""
        tag = Tag.objects.create(name='Test Tag')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Tag.objects.all().count(), 1)

    # ***_STAFF USERS TESTS_*** #

    def staff_create_tag_success(self):
        """Test staff user create tag success."""
        payload = {"name": "Test Tag"}

        res = self.staff_client.post(TAGS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.all().count(), 1)

    def staff_update_tag_success(self):
        """Test staff users updating tag success."""
        tag = Tag.objects.create(name='Test Tag')

        url = detail_url(tag.id)
        payload = {"name": "New Name"}
        res = self.staff_client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def staff_delete_tag_success(self):
        """Test staff user can delete a tag from database."""
        tag = Tag.objects.create(name="Tag")

        url = detail_url(tag.id)
        res = self.staff_client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tag.objecst.all().count(), 0)
