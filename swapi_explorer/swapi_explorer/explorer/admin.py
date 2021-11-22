"""Explorer admin module."""
from django.contrib import admin

# Register your models here.
from swapi_explorer.explorer.models import PeopleCollection


@admin.register(PeopleCollection)
class PeopleCollectionAdmin(admin.ModelAdmin):
    """People collection admin."""

    list_display = ["created"]
