from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

admin.site.site_header = 'ГлавТурник KG — Админ панель'
admin.site.site_title = 'ГлавТурник KG'
admin.site.index_title = 'Управление сайтом'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'name', 'name_kg', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']

    fieldsets = [
        ('Основное', {
            'fields': ('emoji', 'slug', 'order'),
        }),
        ('Название', {
            'fields': ('name', 'name_kg'),
            'description': 'Заполните название на обоих языках',
        }),
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['preview_image', 'name', 'category', 'price_display', 'is_hit', 'order']
    list_editable = ['is_hit', 'order']
    list_filter = ['category', 'is_hit']
    search_fields = ['name', 'name_kg']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category__order', 'order']

    fieldsets = [
        ('Основное', {
            'fields': ('category', 'slug', 'price', 'image', 'is_hit', 'order'),
        }),
        ('Русский язык', {
            'fields': ('name', 'description'),
        }),
        ('Кыргызский язык', {
            'fields': ('name_kg', 'description_kg'),
            'description': 'Необязательно — если не заполнено, используется русский текст',
        }),
    ]

    @admin.display(description='Фото')
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="/static/{}" style="height:48px;border-radius:6px;object-fit:cover;">', obj.image)
        return '—'

    @admin.display(description='Цена')
    def price_display(self, obj):
        return f'{obj.price:,} сом'.replace(',', ' ')
