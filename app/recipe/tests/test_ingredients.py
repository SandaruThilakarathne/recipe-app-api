from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingreedient, Recipe
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

    def test_create_ingreedient_successfull(self):
        """ Test creating a new tag """
        paylaod = {'name': 'test_ingreedient'}
        self.client.post(INGREEDIENTS_URL, paylaod)

        exists = Ingreedient.objects.filter(
            user=self.user,
            name=paylaod['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingreedient_invalid(self):
        """ test creating a tag with invalida payload """
        paylaod = {'name': ''}
        res = self.client.post(INGREEDIENTS_URL, paylaod)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ingreedient_filter(self):
        """ testing tags filtering """
        ing1 = Ingreedient.objects.create(user=self.user, name='ing432')
        ing2 = Ingreedient.objects.create(user=self.user, name='ing')

        recipe = Recipe.objects.create(
            title='Inasfaf',
            time_miniutes=60,
            price=20.00,
            user=self.user
        )

        recipe.ingreedient.add(ing1)

        res = self.client.get(INGREEDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngreedientSerializer(ing1)
        serializer2 = IngreedientSerializer(ing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retreave_ingreedient_assigned_unique(self):
        """ Test filtering tags by assigned returns unique items """
        ing = Ingreedient.objects.create(user=self.user, name='yasgsda')
        Ingreedient.objects.create(user=self.user, name='asdasfgasf')
        recipe1 = Recipe.objects.create(
            title='Pancake',
            time_miniutes=60,
            price=20.00,
            user=self.user
        )
        recipe1.ingreedient.add(ing)

        recipe2 = Recipe.objects.create(
            title='Bath hitto',
            time_miniutes=2,
            price=3.00,
            user=self.user
        )
        recipe2.ingreedient.add(ing)

        res = self.client.get(INGREEDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
