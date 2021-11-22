"""Explorer urls."""
from django.urls import path

from swapi_explorer.explorer import views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "people-collections/",
        views.PeopleCollectionListView.as_view(),
        name="people-collections",
    ),
    path(
        "people-collections/<int:pk>/",
        views.PeopleCollectionDetailView.as_view(),
        name="people-collection-details",
    ),
    path(
        "people-collections/group-by/<int:pk>/",
        views.PeopleCollectionGroupByView.as_view(),
        name="people-collection-group-by",
    ),
]
