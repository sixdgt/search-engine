from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Publication, Author

admin.site.register(Publication)
admin.site.register(Author)