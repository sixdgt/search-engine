from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Publication(models.Model):
    title = models.CharField(max_length=200)
    abstract = models.TextField(null=True, blank=True)
    link = models.URLField(unique=True)
    published_date = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['link']),
        ]

    def __str__(self):
        return self.title

class Author(models.Model):
    name = models.CharField(max_length=100)
    profile_url = models.URLField(max_length=200)
    publications = models.ManyToManyField(Publication, related_name='authors')
    def __str__(self):
        return self.name