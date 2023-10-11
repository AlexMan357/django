from django.urls import path
from .views import BasedView, ArticleDetailView, LatestArticlesFeed

app_name = "BlogApp"

urlpatterns = [
    path("articles/", BasedView.as_view(), name='articles'),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name='article'),
    path("articles/latest/feed/", LatestArticlesFeed(), name='articles-feed'),
]