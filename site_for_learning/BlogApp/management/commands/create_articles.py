from typing import Sequence

from django.core.management import BaseCommand
from BlogApp.models import Article, Author, Tag, Category
from django.db import transaction


class Command(BaseCommand):
    """
    Create orders
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create articles with tags")
        author = Author.objects.get(id=2)
        category = Category.objects.get(id=1)
        tags: Sequence[Tag] = Tag.objects.only("id").all()

        article, created = Article.objects.get_or_create(
            title='about_animals',
            author=author,
            content='animals',
            pub_date='2022-10-01',
            category=category,
        )
        for tag in tags:
            article.tags.add(tag)
        article.save()

        self.stdout.write(self.style.SUCCESS("Done"))
