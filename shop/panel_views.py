from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Category, Product


def staff_required(fn):
    from functools import wraps
    @wraps(fn)
    def inner(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return redirect('panel_login')
        return fn(request, *args, **kwargs)
    return inner


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
        'cats': Category.objects.order_by('order'),
    })


@staff_required
def panel_category_new(request):
    error = None
    data = {}
    if request.method == 'POST':
        data = request.POST
        name = data.get('name', '').strip()
        slug_val = data.get('slug', '').strip() or slugify(name)
        if not name:
            error = 'Укажите название на русском'
        elif Category.objects.filter(slug=slug_val).exists():
            error = f'Slug «{slug_val}» уже занят'
        else:
            Category.objects.create(
                name=name,
                name_kg=data.get('name_kg', '').strip(),
                emoji=data.get('emoji', '🏋️').strip() or '🏋️',
                order=int(data.get('order') or 0),
                slug=slug_val,
            )
            return redirect('panel_categories')
    return render(request, 'panel/category_form.html', {'active': 'categories', 'action': 'new', 'data': data, 'error': error})


@staff_required
def panel_category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug_val = request.POST.get('slug', '').strip() or cat.slug
        if not name:
            error = 'Укажите название на русском'
        elif slug_val != cat.slug and Category.objects.filter(slug=slug_val).exists():
            error = f'Slug «{slug_val}» уже занят'
        else:
            cat.name = name
            cat.name_kg = request.POST.get('name_kg', '').strip()
            cat.emoji = request.POST.get('emoji', '🏋️').strip() or '🏋️'
            cat.order = int(request.POST.get('order') or 0)
            cat.slug = slug_val
            cat.save()
            return redirect('panel_categories')
    return render(request, 'panel/category_form.html', {'active': 'categories', 'action': 'edit', 'cat': cat, 'error': error})


@staff_required
def panel_category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
    return redirect('panel_categories')


# ── Products ────────────────────────────────────────────────────────────────

@staff_required
def panel_products(request):
    qs = Product.objects.select_related('category').order_by('category__order', 'order')
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
        'cats': Category.objects.order_by('order'),
        'cat_slug': cat_slug,
        'q': q,
    })


@staff_required
def panel_product_new(request):
    error = None
    data = {}
    cats = Category.objects.order_by('order')
    if request.method == 'POST':
        data = request.POST
        name = data.get('name', '').strip()
        slug_val = data.get('slug', '').strip() or slugify(name)
        if not name:
            error = 'Укажите название на русском'
        elif not data.get('category'):
            error = 'Выберите категорию'
        elif Product.objects.filter(slug=slug_val).exists():
            error = f'Slug «{slug_val}» уже занят'
        else:
            try:
                Product.objects.create(
                    name=name,
                    name_kg=data.get('name_kg', '').strip(),
                    slug=slug_val,
                    category_id=data['category'],
                    price=int(data.get('price') or 0),
                    image=data.get('image', '').strip(),
                    description=data.get('description', '').strip(),
                    description_kg=data.get('description_kg', '').strip(),
                    is_hit='is_hit' in data,
                    order=int(data.get('order') or 0),
                )
                return redirect('panel_products')
            except Exception as e:
                error = str(e)
    return render(request, 'panel/product_form.html', {'active': 'products', 'action': 'new', 'cats': cats, 'data': data, 'error': error})


@staff_required
def panel_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    error = None
    cats = Category.objects.order_by('order')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug_val = request.POST.get('slug', '').strip() or product.slug
        if not name:
            error = 'Укажите название на русском'
        elif slug_val != product.slug and Product.objects.filter(slug=slug_val).exists():
            error = f'Slug «{slug_val}» уже занят'
        else:
            product.name = name
            product.name_kg = request.POST.get('name_kg', '').strip()
            product.slug = slug_val
            product.category_id = request.POST.get('category', product.category_id)
            product.price = int(request.POST.get('price') or product.price)
            product.image = request.POST.get('image', '').strip()
            product.description = request.POST.get('description', '').strip()
            product.description_kg = request.POST.get('description_kg', '').strip()
            product.is_hit = 'is_hit' in request.POST
            product.order = int(request.POST.get('order') or 0)
            product.save()
            return redirect('panel_products')
    return render(request, 'panel/product_form.html', {'active': 'products', 'action': 'edit', 'product': product, 'cats': cats, 'error': error})


@staff_required
def panel_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
    return redirect('panel_products')
