from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingreedient, Recipe
from recipe import serializers


class BaseRecipeViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for the current authenticated user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializers):
        """ Create a new object """
        serializers.save(user=self.request.user)


class TagViewSet(BaseRecipeViewSet):
    """ Manage tags in database """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngreedientViewSet(BaseRecipeViewSet):
    """ manage ingreedients in the database """
    queryset = Ingreedient.objects.all()
    serializer_class = serializers.IngreedientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ Manage recipes in the db """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ Return objects for the current authenticated user only """
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ Return appropriate serializer class """
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class
