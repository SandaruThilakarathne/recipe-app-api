from rest_framework import serializers
from core.models import Tag, Ingreedient


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
