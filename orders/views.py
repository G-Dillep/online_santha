from django.shortcuts import render

def order_list_view(request):
    return render(request, 'orders/list.html')
