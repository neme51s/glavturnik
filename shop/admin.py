from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_hit', 'order']
    list_filter = ['category', 'is_hit']
    list_editable = ['is_hit', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']
