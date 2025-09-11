from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm, ProductFilterForm

def product_list_view(request):
    products = Product.objects.filter(status='available').select_related('farmer', 'category')
    categories = Category.objects.all()
    filter_form = ProductFilterForm(request.GET)
    
    # Apply filters
    if filter_form.is_valid():
        if filter_form.cleaned_data['category']:
            products = products.filter(category=filter_form.cleaned_data['category'])
        
        if filter_form.cleaned_data['location']:
            products = products.filter(location__icontains=filter_form.cleaned_data['location'])
        
        if filter_form.cleaned_data['min_price']:
            products = products.filter(price_per_unit__gte=filter_form.cleaned_data['min_price'])
        
        if filter_form.cleaned_data['max_price']:
            products = products.filter(price_per_unit__lte=filter_form.cleaned_data['max_price'])
        
        if filter_form.cleaned_data['is_organic']:
            products = products.filter(is_organic=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(farmer__first_name__icontains=search_query) |
            Q(farmer__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'filter_form': filter_form,
        'search_query': search_query,
        'total_products': products.count(),
    }
    return render(request, 'products/list.html', context)

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(
        category=product.category,
        status='available'
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)

@login_required
def add_product_view(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can add products.')
        return redirect('products:list')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm()
    
    return render(request, 'products/add.html', {'form': form})

@login_required
def edit_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products:detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit.html', {'form': form, 'product': product})

@login_required
def delete_product_view(request, pk):
    product = get_object_or_404(Product, pk=pk, farmer=request.user)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('dashboard:home')
    
    return render(request, 'products/delete.html', {'product': product})

@login_required
def my_products_view(request):
    if request.user.user_type != 'farmer':
        messages.error(request, 'Only farmers can view this page.')
        return redirect('products:list')
    
    products = Product.objects.filter(farmer=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_products': products.count(),
    }
    return render(request, 'products/my_products.html', context)
