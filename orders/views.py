from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm, AddToCartForm
import json

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, status='available')
    
    if product.farmer == request.user:
        messages.error(request, "You cannot buy your own product.")
        return redirect('products:detail', pk=product_id)
    
    form = AddToCartForm(request.POST)
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        
        if quantity > product.quantity_available:
            messages.error(request, f"Only {product.quantity_available} {product.unit} available.")
            return redirect('products:detail', pk=product_id)
        
        if quantity < product.minimum_order:
            messages.error(request, f"Minimum order quantity is {product.minimum_order} {product.unit}.")
            return redirect('products:detail', pk=product_id)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Get or create cart item
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Update existing cart item
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.quantity_available:
                messages.error(request, f"Cannot add more. Total would exceed available quantity.")
                return redirect('products:detail', pk=product_id)
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f"Updated quantity to {cart_item.quantity} {product.unit}.")
        else:
            messages.success(request, f"Added {quantity} {product.unit} of {product.name} to cart.")
        
        return redirect('orders:cart')
    else:
        messages.error(request, "Invalid quantity.")
        return redirect('products:detail', pk=product_id)

@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'product__farmer').all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/cart.html', context)

@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    
    try:
        data = json.loads(request.body)
        new_quantity = float(data.get('quantity', 0))
        
        if new_quantity <= 0:
            cart_item.delete()
            return JsonResponse({'status': 'removed'})
        
        if new_quantity > cart_item.product.quantity_available:
            return JsonResponse({
                'status': 'error',
                'message': f'Only {cart_item.product.quantity_available} {cart_item.product.unit} available'
            })
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        return JsonResponse({
            'status': 'updated',
            'total_price': float(cart_item.total_price),
            'cart_total': float(cart_item.cart.total_amount)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"Removed {product_name} from cart.")
    return redirect('orders:cart')

@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product', 'product__farmer').all()
        
        if not cart_items:
            messages.info(request, "Your cart is empty.")
            return redirect('products:list')
    except Cart.DoesNotExist:
        messages.info(request, "Your cart is empty.")
        return redirect('products:list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.buyer = request.user
            order.total_amount = cart.total_amount
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    farmer=cart_item.product.farmer,
                    quantity=cart_item.quantity,
                    price_per_unit=cart_item.product.price_per_unit,
                    total_price=cart_item.total_price
                )
                
                # Update product quantity
                product = cart_item.product
                product.quantity_available -= cart_item.quantity
                if product.quantity_available <= 0:
                    product.status = 'sold'
                product.save()
            
            # Clear cart
            cart.delete()
            
            messages.success(request, f"Order {order.order_number} placed successfully!")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Check permissions
    if request.user != order.buyer and not any(item.farmer == request.user for item in order.items.all()):
        messages.error(request, "You don't have permission to view this order.")
        return redirect('orders:order_list')
    
    order_items = order.items.select_related('product', 'farmer').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_list_view(request):
    if request.user.user_type == 'farmer':
        # Show orders for farmer's products
        orders = Order.objects.filter(items__farmer=request.user).distinct().order_by('-created_at')
    else:
        # Show buyer's orders
        orders = request.user.orders.all()
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_type': request.user.user_type,
    }
    return render(request, 'orders/order_list.html', context)

@login_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Only farmers who have items in this order can update status
    if not order.items.filter(farmer=request.user).exists():
        messages.error(request, "You don't have permission to update this order.")
        return redirect('orders:order_detail', order_id=order_id)
    
    new_status = request.POST.get('status')
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"Order status updated to {order.get_status_display()}.")
    else:
        messages.error(request, "Invalid status.")
    
    return redirect('orders:order_detail', order_id=order_id)
