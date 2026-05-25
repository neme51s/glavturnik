from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

admin.site.site_header = 'ГлавТурник KG'
admin.site.site_title = 'ГлавТурник KG'
admin.site.index_title = 'Управление сайтом'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_kg']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_hit']
    list_filter = ['category', 'is_hit']
    list_editable = ['is_hit']
    ordering = ['-is_hit', 'name']
