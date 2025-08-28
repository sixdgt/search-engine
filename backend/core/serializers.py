from rest_framework import serializers
from .models import Publication, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'email']

class PublicationSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Publication
        fields = ['id', 'title', 'abstract', 'publication_date', 'authors']