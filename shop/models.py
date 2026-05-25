from django.db import models


class Category(models.Model):
    name = models.CharField('Название (рус.)', max_length=200)
    name_kg = models.CharField('Название (кырг.)', max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    emoji = models.CharField('Эмодзи', max_length=10, default='🏋️')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name='Категория'
    )
    name = models.CharField('Название', max_length=200)
    name_kg = models.CharField('Название (кырг.)', max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    price = models.PositiveIntegerField('Цена (сом)')
    image = models.CharField('Изображение', max_length=200, blank=True)
    description = models.TextField('Описание', blank=True)
    description_kg = models.TextField('Описание (кырг.)', blank=True)
    is_hit = models.BooleanField('Хит продаж', default=False)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def price_formatted(self):
        return f'{self.price:,}'.replace(',', ' ')
