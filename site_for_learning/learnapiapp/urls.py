from django.urls import path

from .views import hello_world_view, GroupsListView

urlpatterns = [
    path('hello/', hello_world_view, name="hello"),
    path('groups/', GroupsListView.as_view(), name="groups"),
]