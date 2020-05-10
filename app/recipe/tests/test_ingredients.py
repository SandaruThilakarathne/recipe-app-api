from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingreedient
from recipe.serializers import IngreedientSerializer

INGREEDIENTS_URL = reverse('recipe:ingreedient-list')


class PublicIngreediantsApiTest(TestCase):
    """ Test the publically available ingreedient api """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login required to access"""
        res = self.client.get(INGREEDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngreedinentApiTest(TestCase):
    """ Test ingreediants retrive by authorised user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "theethz@hmail.com",
            "testing123"
        )
        self.client.force_authenticate(self.user)

    def test_retrive_ingreedients(self):
        """ test retreiving a list of ingreedients"""
        Ingreedient.objects.create(user=self.user, name='Kale')
        Ingreedient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREEDIENTS_URL)
        ingreedient = Ingreedient.objects.all().order_by('-name')
        serializer = IngreedientSerializer(ingreedient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """ Test that ingreedients for the authentication user
        are returned """

        user2 = get_user_model().objects.create_user(
            "othere@gmail.com",
            "testpass"
        )
        Ingreedient.objects.create(user=user2, name='Vinigere')
        ingredient = Ingreedient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGREEDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_tag_successfull(self):
        """ Test creating a new tag """
        paylaod = {'name': 'test_ingreedient'}
        self.client.post(INGREEDIENTS_URL, paylaod)

        exists = Ingreedient.objects.filter(
            user=self.user,
            name=paylaod['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """ test creating a tag with invalida payload """
        paylaod = {'name': ''}
        res = self.client.post(INGREEDIENTS_URL, paylaod)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
