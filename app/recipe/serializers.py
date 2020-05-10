from rest_framework import serializers
from core.models import Tag, Ingreedient, Recipe


class TagSerializer(serializers.ModelSerializer):
    """ Serializer for tag object """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngreedientSerializer(serializers.ModelSerializer):
    """ Serializers for ingreedient object """
    class Meta:
        model = Ingreedient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """ Serialize a recipe """
    ingreedient = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingreedient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingreedient', 'tags', 'time_miniutes',
                  'price', 'link')

        read_only_fields = ('id',)
