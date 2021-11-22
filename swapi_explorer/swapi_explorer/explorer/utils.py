import os
import uuid
from typing import Optional

from django.conf import settings


def get_random_filename(extension: str = "csv") -> str:
    return f"{uuid.uuid4().hex}.{extension}"


def collection_upload_to(instance, filename: Optional[str] = None) -> str:
    filename = filename or get_random_filename()
    return os.path.join("collections", instance.__class__.__name__.lower(), filename)


def get_full_collection_upload_to(instance, filename: Optional[str] = None) -> str:
    return os.path.join(
        settings.MEDIA_ROOT, collection_upload_to(instance=instance, filename=filename)
    )
