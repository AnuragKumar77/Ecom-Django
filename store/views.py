from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category = categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')    # ?page=2 in url
        paged_products = paginator.get_page(page) # store 6 products in a page
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')    # ?page=2 in url
        paged_products = paginator.get_page(page) # store 6 products in a page
        product_count = products.count()
    context = {
        # 'products': products,
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug = product_slug) #categoory__slug fetch from category slug
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists() #cart__cart_id is to get cart id from card using foriegn key.
        
    except Exception as e :
        raise e 
    
    context = { 
        'single_product': single_product,
        'in_cart': in_cart,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
            context = {
                'products':products,
                'product_count':product_count, 
            }
    return render(request, 'store/store.html', context)