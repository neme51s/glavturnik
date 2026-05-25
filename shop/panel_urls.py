from django.urls import path
from . import panel_views as v

urlpatterns = [
    path('',                          v.panel_login,           name='panel_login'),
    path('logout/',                   v.panel_logout,          name='panel_logout'),
    path('dashboard/',                v.panel_dashboard,       name='panel_dashboard'),

    path('categories/',               v.panel_categories,      name='panel_categories'),
    path('categories/new/',           v.panel_category_new,    name='panel_category_new'),
    path('categories/<int:pk>/edit/', v.panel_category_edit,   name='panel_category_edit'),
    path('categories/<int:pk>/delete/',v.panel_category_delete,name='panel_category_delete'),

    path('products/',                 v.panel_products,        name='panel_products'),
    path('products/new/',             v.panel_product_new,     name='panel_product_new'),
    path('products/<int:pk>/edit/',   v.panel_product_edit,    name='panel_product_edit'),
    path('products/<int:pk>/delete/', v.panel_product_delete,  name='panel_product_delete'),
]
