"""Explorer views module."""
import time
from typing import Dict, List

import petl
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, TemplateView
from petl import Table
from petl.util.base import DataView

from swapi_explorer.explorer.importers import StarWarsImporter
from swapi_explorer.explorer.models import PeopleCollection


def index(request: WSGIRequest):
    """Index view."""
    return render(request, "explorer/index.html")


class CollectionListView(ListView):
    """Base collection list view."""

    template_name = "explorer/collection_list.html"
    details_view_name = None

    def get_context_data(self, **kwargs):
        """Include both Star Wars people and pagination data."""
        context: Dict = super().get_context_data(**kwargs)
        context["details_view_name"] = self.details_view_name
        return context


class PeopleCollectionListView(CollectionListView):
    """People collection list view."""

    details_view_name = "people-collection-details"
    model = PeopleCollection
    queryset = PeopleCollection.objects.order_by("-created")

    def post(self, request: WSGIRequest, *args, **kwargs):
        """Import people collection."""
        try:
            start_time: float = time.time()
            per_page: bool = bool(request.POST.get("per_page"))
            collection: PeopleCollection = (
                StarWarsImporter().import_people_page_by_page()
                if per_page
                else StarWarsImporter().import_people()
            )
            total_seconds: float = time.time() - start_time
            messages.success(
                request,
                f"New collection - {collection} - downloaded in {total_seconds} seconds, with per page alg={per_page}.",
            )
        except:  # noqa
            messages.error(
                request, "There were some problems with importing new collection."
            )

        return redirect("people-collections")


class CollectionDetailView(DetailView):
    """Base collection like details view."""

    PAGE_SIZE: int = 10

    context_object_name = "collection"
    template_name = "explorer/collection_detail.html"
    group_by_view_name = None

    def get_context_data(self, **kwargs):
        """Include both Star Wars people and pagination data."""
        context: Dict = super().get_context_data(**kwargs)

        table: Table = petl.fromcsv(context["collection"].csv_file)

        current_page: int = int(self.request.GET.get("page", 1))
        total_count: int = petl.nrows(table)
        has_next: bool = current_page * self.PAGE_SIZE < total_count
        next_page: int = current_page + 1
        visible_entries: int = current_page * self.PAGE_SIZE

        context.update(
            {
                "current_page": current_page,
                "total_count": total_count,
                "has_next": has_next,
                "next_page": next_page,
                "headers": petl.header(table),
                "data": petl.data(table, visible_entries),
                "group_by_view": self.group_by_view_name,
            }
        )
        return context


class PeopleCollectionDetailView(CollectionDetailView):
    """People collection details view."""

    model = PeopleCollection
    group_by_view_name = "people-collection-group-by"


class CollectionGroupByView(TemplateView):
    """Group by collection values and display each group count."""

    model = None
    template_name: str = "explorer/collection_group_by.html"
    details_view_name = None

    def get_context_data(self, pk, **kwargs):
        """Add all necessary data to the context."""
        context: dict = super().get_context_data(**kwargs)
        context["details_view_name"] = self.details_view_name
        context["object"] = get_object_or_404(self.model, pk=pk)
        table = petl.fromcsv(context["object"].csv_file)
        context["headers"] = petl.header(table)

        group_by_str = self.request.GET.get("group_by", "")

        if not group_by_str:
            context["data"] = []
            context["grouped_data_headers"] = context["headers"]
            messages.warning(self.request, "Please select any column to group data.")
        else:
            group_by: List[str] = [
                group_by_column
                for group_by_column in group_by_str.split(",")
                if group_by_column and group_by_column in context["headers"]
            ]
            data: DataView = (
                petl.valuecounts(table, *group_by).cutout("frequency").data()
            )
            context["data"] = data
            context["grouped_data_headers"] = [*group_by, "count"]
        return context


class PeopleCollectionGroupByView(CollectionGroupByView):
    """People collection group by view."""

    model = PeopleCollection
    details_view_name = "people-collection-details"
