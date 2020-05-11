from django.db import models
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.conf import settings


def recipe_image_file_path(instance, file_name):
    """ Generate file path to recipe image """
    ext = file_name.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('upload/recipe', filename)


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """ Create and saves a new user """

        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create and save new superuser """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model that support using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """ Tag to be use for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingreedient(models.Model):
    """ Ingreedient to be used in recipe """
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ recipe object """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_miniutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingreedient = models.ManyToManyField('Ingreedient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
