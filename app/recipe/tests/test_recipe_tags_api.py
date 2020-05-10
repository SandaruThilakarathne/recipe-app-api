from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    """ Test the publicly available tags """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test login required for retriving tags """
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagesApiTest(TestCase):
    """ test the authorized user tags API """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@theesh.com',
            'testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """ Test retriving tags """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)
        tag = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tag, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """ check tags are limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test@theesh24.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
