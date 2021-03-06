from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email='theesh123@gmail.com', password='testpass'):
    """ Create sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        """ Test creating a new user with an email is successfull """
        email = "test@testingsan.com"
        password = "Test@pass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ test the email for the user normalized """
        email = "test@TESTSfdas.com"
        user = get_user_model().objects.create_user(email, "Test@pass123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raise error"""
        password = "test123as"

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, password)

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser('test@123.com',
                                                         "Test@pass123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """ Test ingredients string representation """
        ingreedient = models.Ingreedient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingreedient), ingreedient.name)

    def test_recipe_str(self):
        """ Test the recipe string representation """
        recepe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_miniutes=5,
            price=5.00,
        )

        self.assertEqual(str(recepe), recepe.title)

    @patch('uuid.uuid4')
    def test_recipe_filename_uuid(self, mock_uuid):
        """ Test that image is saved in the correct
        Location """
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'upload/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
