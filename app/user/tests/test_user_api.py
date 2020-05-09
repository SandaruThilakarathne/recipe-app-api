from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
UPDATE_USER_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test the users API (public) """

    def sertUp(self):
        self.client = APIClient()

    def create_valid_user_success(self):
        """ Test creating user with payload is successfulll """
        payload = {
            'email': 'test@tasn.com',
            'password': 'testpass',
            'name': "Test name"
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn("password", res.data)

    def test_user_exist(self):
        """ Testing creating user that already exist """
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'pw',
            'name': 'Test',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 charactors"""
        payload = {
            'email': 'test@londonappdev.com',
            'password': 'p',
            'name': 'Test',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """ Testing token creation for the user """

        payload = {
            'email': 'nila@gmail.com',
            'password': 'test@123'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Testing weather the token is generaating for
        the invalid credentials """
        create_user(email='test@testing.com', password="testpass")
        payload = {
            'email': 'test@testing.com',
            'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """ Test that token is not created if user doesn't exist """
        payload = {
            'email': '123@1234214.com',
            'password': '123343'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password_field_create_token(self):
        """ Testing weather the token generates with
        missing passowrd """
        res = self.client.post(TOKEN_URL, {'email': "one", 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retreve_user_unauthorized(self):
        """ Testing weather the unauthorized users
        can access this rout """
        res = self.client.get(UPDATE_USER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """ test api which required authentication """

    def setUp(self):
        self.user = create_user(
            email='theesh123@gmail.com',
            password='testpass',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retreve_profile_success(self):
        """ Test retreving profile for loged in user """
        res = self.client.get(UPDATE_USER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """ Test that post is not allowed """
        res = self.client.post(UPDATE_USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ test updating the  user profile for authenticated user """
        payload = {
            "name": "newname",
            "password": "newpass123",
        }
        res = self.client.patch(UPDATE_USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
