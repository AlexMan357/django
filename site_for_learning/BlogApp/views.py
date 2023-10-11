from django.contrib.syndication.views import Feed
from django.db.models import Prefetch
from django.views.generic import ListView, DetailView
from .models import Article, Author
from django.urls import reverse, reverse_lazy

class BasedView(ListView):
    template_name = 'BlogApp/article-list.html'
    context_object_name = "all_articles"
    # query_author = Author.objects.only('name')

    queryset = (
                Article.objects
                .select_related("author", "category")
                .prefetch_related("tags")
                .defer("content")
                # .all()
                )

    queryset = queryset.filter(pub_date__isnull=False).order_by("-pub_date")

class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and additions blog articles"
    link = reverse_lazy("BlogApp:articles")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    # def item_link(self, item: Article):
    #     return reverse("BlogApp:article", kwargs={"pk": item.pk})

