
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list_view, name='list'),
    path('<int:pk>/', views.product_detail_view, name='detail'),
    path('add/', views.add_product_view, name='add'),
    path('<int:pk>/edit/', views.edit_product_view, name='edit'),
    path('<int:pk>/delete/', views.delete_product_view, name='delete'),
    path('my-products/', views.my_products_view, name='my_products'),
]
