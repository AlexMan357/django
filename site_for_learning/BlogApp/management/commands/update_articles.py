from django.core.management import BaseCommand
from BlogApp.models import Article


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Bulk update articles")
        result = Article.objects.filter(
            title__contains="animals"
        ).update(pub_date='2023-06-01')

        print(result)

        self.stdout.write(self.style.SUCCESS("Done"))
