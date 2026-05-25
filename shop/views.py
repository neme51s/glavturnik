from django.shortcuts import render
from .models import Category, Product


def index(request):
    categories = Category.objects.prefetch_related('products').all()
    hits = Product.objects.filter(is_hit=True).select_related('category')
    all_products = Product.objects.select_related('category').order_by('-is_hit', 'name')
    return render(request, 'shop/index.html', {
        'categories': categories,
        'hits': hits,
        'all_products': all_products,
    })
