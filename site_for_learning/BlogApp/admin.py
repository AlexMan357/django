from django.contrib import admin

from BlogApp.models import Article


# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'content', 'pub_date', 'author', 'category'
