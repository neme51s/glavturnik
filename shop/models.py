from django.db import models
from django.utils.text import slugify


def _unique_slug(model, name, exclude_pk=None):
    base = slugify(name) or 'item'
    slug, n = base, 1
    qs = model.objects.filter(slug=slug)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    while qs.exists():
        slug = f'{base}-{n}'
        n += 1
        qs = model.objects.filter(slug=slug)
        if exclude_pk:
            qs = qs.exclude(pk=exclude_pk)
    return slug


class Category(models.Model):
    name    = models.CharField('Название (рус.)', max_length=200)
    name_kg = models.CharField('Название (кырг.)', max_length=200, blank=True)
    slug    = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Category, self.name, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name        = models.CharField('Название (рус.)', max_length=200)
    name_kg     = models.CharField('Название (кырг.)', max_length=200, blank=True)
    slug        = models.SlugField(unique=True, blank=True)
    price       = models.PositiveIntegerField('Цена (сом)')
    image       = models.CharField('Изображение', max_length=500, blank=True)
    description    = models.TextField('Описание (рус.)', blank=True)
    description_kg = models.TextField('Описание (кырг.)', blank=True)
    is_hit      = models.BooleanField('Хит продаж', default=False)

    class Meta:
        ordering = ['-is_hit', 'name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Product, self.name, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def price_formatted(self):
        return f'{self.price:,}'.replace(',', ' ')
