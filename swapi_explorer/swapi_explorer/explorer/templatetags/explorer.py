"""Explorer tempate tags."""
import os
from typing import List

from django import template
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import FileField

register = template.Library()


@register.filter
def filename(file: FileField):
    """Print file filename."""
    return os.path.basename(file.name)


@register.simple_tag
def get_group_by_url(value: str, request: WSGIRequest, key: str = "group_by") -> str:
    """Get new URL based on whether or not param is in kwarg"""
    group_by_param: str = request.GET.get(key, "")
    group_by_list: List[str] = group_by_param.split(",")
    if group_by_list:
        if value in group_by_list:
            group_by_list.remove(value)
        else:
            group_by_list.append(value)
    else:
        group_by_list.append(value)

    return f"{request.path}?{key}={','.join(group_by_list)}"
