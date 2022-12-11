from django.shortcuts import render
from store.models import Product


def home(request):
    product = Product.objects.all().filter(is_available=True)[:8]
    context = {
        'products':product
    }
    return render(request,"home.html",context)