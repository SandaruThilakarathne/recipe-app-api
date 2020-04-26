from django.test import TestCase
from django.contrib.auth import get_user_model


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