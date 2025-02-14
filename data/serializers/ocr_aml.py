from rest_framework.serializers import (
    FileField,
    ImageField,
    ModelSerializer,
    Serializer,
)

from data.models import Person


class PassportImageSerializer(Serializer):
    image = ImageField()

class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        