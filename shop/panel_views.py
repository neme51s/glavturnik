import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from .models import Category, Product


def staff_required(fn):
    from functools import wraps
    @wraps(fn)
    def inner(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect('panel_login')
        return fn(request, *args, **kwargs)
    return inner


def _upload_image(file):
    import cloudinary.uploader
    result = cloudinary.uploader.upload(file, folder='glavturnik')
    return result['secure_url']


def panel_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('panel_dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user and user.is_staff:
            login(request, user)
            return redirect('panel_dashboard')
        error = 'Неверный логин или пароль'
    return render(request, 'panel/login.html', {'error': error})


def panel_logout(request):
    logout(request)
    return redirect('panel_login')


@staff_required
def panel_dashboard(request):
    return render(request, 'panel/dashboard.html', {
        'active': 'dashboard',
        'total_cats': Category.objects.count(),
        'total_products': Product.objects.count(),
        'total_hits': Product.objects.filter(is_hit=True).count(),
        'recent': Product.objects.select_related('category').order_by('-id')[:5],
    })


# ── Categories ──────────────────────────────────────────────────────────────

@staff_required
def panel_categories(request):
    return render(request, 'panel/categories.html', {
        'active': 'categories',
        'cats': Category.objects.order_by('name'),
    })


@staff_required
def panel_category_new(request):
    error = None
    obj = {}
    if request.method == 'POST':
        obj = request.POST
        name = obj.get('name', '').strip()
        if not name:
            error = 'Укажите название на русском'
        else:
            Category.objects.create(
                name=name,
                name_kg=obj.get('name_kg', '').strip(),
            )
            return redirect('panel_categories')
    return render(request, 'panel/category_form.html', {'active': 'categories', 'action': 'new', 'obj': obj, 'error': error})


@staff_required
def panel_category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            error = 'Укажите название на русском'
        else:
            cat.name = name
            cat.name_kg = request.POST.get('name_kg', '').strip()
            cat.save()
            return redirect('panel_categories')
        obj = request.POST
    else:
        obj = {'name': cat.name, 'name_kg': cat.name_kg}
    return render(request, 'panel/category_form.html', {'active': 'categories', 'action': 'edit', 'cat': cat, 'obj': obj, 'error': error})


@staff_required
def panel_category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
    return redirect('panel_categories')


# ── Products ────────────────────────────────────────────────────────────────

@staff_required
def panel_products(request):
    qs = Product.objects.select_related('category').order_by('-is_hit', 'name')
    cat_slug = request.GET.get('cat', '')
    q = request.GET.get('q', '')
    if cat_slug:
        qs = qs.filter(category__slug=cat_slug)
    if q:
        qs = qs.filter(name__icontains=q)
    page_obj = Paginator(qs, 20).get_page(request.GET.get('page', 1))
    return render(request, 'panel/products.html', {
        'active': 'products',
        'page_obj': page_obj,
        'cats': Category.objects.order_by('name'),
        'cat_slug': cat_slug,
        'q': q,
    })


@staff_required
def panel_product_new(request):
    error = None
    obj = {'price': 0}
    cats = Category.objects.order_by('name')
    if request.method == 'POST':
        obj = request.POST
        name = obj.get('name', '').strip()
        if not name:
            error = 'Укажите название на русском'
        elif not obj.get('category'):
            error = 'Выберите категорию'
        else:
            try:
                image_url = ''
                if request.FILES.get('image'):
                    image_url = _upload_image(request.FILES['image'])
                Product.objects.create(
                    name=name,
                    name_kg=obj.get('name_kg', '').strip(),
                    category_id=obj['category'],
                    price=int(obj.get('price') or 0),
                    image=image_url,
                    description=obj.get('description', '').strip(),
                    description_kg=obj.get('description_kg', '').strip(),
                    is_hit='is_hit' in obj,
                )
                return redirect('panel_products')
            except Exception as e:
                error = str(e)
    return render(request, 'panel/product_form.html', {'active': 'products', 'action': 'new', 'cats': cats, 'obj': obj, 'error': error})


@staff_required
def panel_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    error = None
    cats = Category.objects.order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            error = 'Укажите название на русском'
        else:
            try:
                if request.FILES.get('image'):
                    product.image = _upload_image(request.FILES['image'])
                product.name = name
                product.name_kg = request.POST.get('name_kg', '').strip()
                product.category_id = request.POST.get('category', product.category_id)
                product.price = int(request.POST.get('price') or product.price)
                product.description = request.POST.get('description', '').strip()
                product.description_kg = request.POST.get('description_kg', '').strip()
                product.is_hit = 'is_hit' in request.POST
                product.save()
                return redirect('panel_products')
            except Exception as e:
                error = str(e)
        obj = request.POST
    else:
        obj = {
            'name': product.name, 'name_kg': product.name_kg,
            'price': product.price, 'image': product.image,
            'description': product.description,
            'description_kg': product.description_kg,
            'is_hit': product.is_hit,
            'category': str(product.category_id),
        }
    return render(request, 'panel/product_form.html', {'active': 'products', 'action': 'edit', 'product': product, 'cats': cats, 'obj': obj, 'error': error})


@staff_required
def panel_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('panel_products')
