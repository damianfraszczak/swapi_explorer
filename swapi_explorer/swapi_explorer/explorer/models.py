"""Explorer models module."""
from django.db import models

from swapi_explorer.explorer.utils import collection_upload_to


class Collection(models.Model):
    """Collection model."""

    created = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to=collection_upload_to)

    def __str__(self):
        return f"{self.created}"

    class Meta:  # noqa: D106
        abstract = True


class PeopleCollection(Collection):
    """People Collection model."""
