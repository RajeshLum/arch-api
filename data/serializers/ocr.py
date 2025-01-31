from rest_framework.serializers import FileField, ImageField, Serializer


class PassportImageSerializer(Serializer):
    image = ImageField()
