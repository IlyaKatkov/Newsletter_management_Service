from django.contrib import admin

from blog.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created', 'is_published')
    search_fields = ('title', 'created',)
    list_filter = ('is_published',)
