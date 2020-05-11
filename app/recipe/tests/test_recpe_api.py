from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

import tempfile
import os

from PIL import Image

from core.models import Recipe, Ingreedient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def image_uplaod_url(recipe_id):
    """ Getting url for image uplaod """
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def detail_url(recipe_id):
    """ Return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])


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


def sampe_tag(user, name="Main course"):
    """ Create and returns a sample tag """
    return Tag.objects.create(user=user, name=name)


def sampe_ingreedient(user, name="Cinnoman"):
    """ Create and returns a sample ingreedient """
    return Ingreedient.objects.create(user=user, name=name)


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

    def test_view_recipe_details(self):
        """ Test viewving a recipe detail """
        recipe = sample_recepe(user=self.user)
        recipe.tags.add(sampe_tag(user=self.user))
        recipe.ingreedient.add(sampe_ingreedient(self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """ Test creating recipe """
        paylaod = {
            "title": "Chocolate cheesecake",
            "time_miniutes": 30,
            "price": 5.00
        }

        res = self.client.post(RECIPE_URL, paylaod)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in paylaod.keys():
            self.assertEqual(paylaod[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ Test creating recipe with tags  """
        tag1 = sampe_tag(user=self.user, name='Vegan')
        tag2 = sampe_tag(user=self.user, name='Dessart')

        payload = {
            'title': 'Avacado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_miniutes': 60,
            'price': 20.00
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingreedients(self):
        """ Test creating recipe with ingreedients """
        Ingreedient1 = sampe_ingreedient(user=self.user, name='Prawns')
        Ingreedient2 = sampe_ingreedient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingreedient': [Ingreedient1.id, Ingreedient2.id],
            'time_miniutes': 20,
            'price': 7.00
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingreedient = recipe.ingreedient.all()
        self.assertEqual(ingreedient.count(), 2)
        self.assertIn(Ingreedient1, ingreedient)
        self.assertIn(Ingreedient2, ingreedient)

    def test_partial_update_recipe(self):
        """ Test updateing recipe with patch """
        recipe = sample_recepe(user=self.user)
        recipe.tags.add(sampe_tag(user=self.user))
        new_tag = sampe_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Chicken tikka',
            'tags': [new_tag.id]
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update(self):
        """ Test update recipe with put """
        recipe = sample_recepe(user=self.user)
        recipe.tags.add(sampe_tag(user=self.user))

        payload = {
            'title': 'Spagehetti carbonara',
            'time_miniutes': 25,
            'price': 5.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_miniutes, payload['time_miniutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecepeImageUploadTest(TestCase):
    """ Test image uploading """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@theesqweh.com',
            'testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.recipe = sample_recepe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_uploading_image(self):
        """ testing valid image upload """
        url = image_uplaod_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad(self):
        """ testing invalid image upload """
        url = image_uplaod_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """ returning recipes by specific tags """
        recope1 = sample_recepe(user=self.user, title="Thai vegi curry")
        recope2 = sample_recepe(user=self.user, title="test thatisad")

        tag1 = sampe_tag(user=self.user, name='Vigan')
        tag2 = sampe_tag(user=self.user, name='vegitarian')
        recope1.tags.add(tag1)
        recope2.tags.add(tag2)

        recope3 = sample_recepe(user=self.user, title="Fish and chips")
        res = self.client.get(
            RECIPE_URL,
            {'tags': f'{tag1.id}, {tag2.id}'}
        )
        serialized1 = RecipeSerializer(recope1)
        serialized2 = RecipeSerializer(recope2)
        serialized3 = RecipeSerializer(recope3)
        self.assertIn(serialized1.data, res.data)
        self.assertIn(serialized2.data, res.data)
        self.assertNotIn(serialized3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """ returning recipes by specific ingreediants """
        recope1 = sample_recepe(user=self.user, title="Thai vegi curry")
        recope2 = sample_recepe(user=self.user, title="test thatisad")

        ingredients1 = sampe_ingreedient(user=self.user, name='Test1234')
        ingredients2 = sampe_ingreedient(
            user=self.user, name='test2344521124365')
        recope1.ingreedient.add(ingredients1)
        recope2.ingreedient.add(ingredients2)

        recope3 = sample_recepe(user=self.user, title="test12e33")
        res = self.client.get(
            RECIPE_URL,
            {'ingreedient': f'{ingredients1.id}, {ingredients2.id}'}
        )
        serialized1 = RecipeSerializer(recope1)
        serialized2 = RecipeSerializer(recope2)
        serialized3 = RecipeSerializer(recope3)
        self.assertIn(serialized1.data, res.data)
        self.assertIn(serialized2.data, res.data)
        self.assertNotIn(serialized3.data, res.data)
