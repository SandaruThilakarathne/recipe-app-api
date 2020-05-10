from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recepe(user, **params):
    """ create and return sample recipes """
    defaults = {
        'title': 'Sample recipe',
        'time_miniutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(
        user=user,
        **defaults
    )


class PublicRecipeAPITest(TestCase):
    """ Test unauthenticated recepe api """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """ Test authenticated recipe API access """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@theesh.com',
            'testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def retreve_recipes(self):
        """ Testing reteving recipes """
        sample_recepe(user=self.user)
        sample_recepe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_are_limited_to_user(self):
        """ Test recipes are only returns according to the user """

        user2 = get_user_model().objects.create_user(
            'test@theesh24.com',
            'testpass'
        )
        sample_recepe(user=user2)
        sample_recepe(user=self.user)
        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
