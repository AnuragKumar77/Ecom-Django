from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from . models import Cart , CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# def add_cart(request, product_id):
#     product = Product.objects.get(id=product_id) # get the product
#     product_variation = []
#     if request.method == "POST":
#         # color = request.POST['color']
#         # size = request.POST['size']
#         # return HttpResponse(color + ' ' + size)
#         # exit()
#         # print(color, size)
#         for item in request.POST:
#             key = item     # color ya anything will be store in key and they value will be store in value.like color = green and size = M
#             value = request.POST[key]
#             # print(key, value)
#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 # print(variation)
#                 product_variation.append(variation)
#             except:
#                 pass

#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))   # get the cart using cart_id present in session
#     except Cart.DoesNotExist:
#         cart = Cart.objects.create(
#             cart_id = _cart_id(request)
#         )

#     cart.save()

#     is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
#     if is_cart_item_exists:
#         cart_item = CartItem.objects.filter(product=product, cart=cart)
#         # existing variations - coming from database
#         # current variations = product variation to check exist or not
#         # cart_id = database

#         ext_var_list = []
#         id = []
#         for item in cart_item:
#             existing_variation = item.variations.all()
#             ext_var_list.append(list(existing_variation))
#             id.append(item.id)

#         print(ext_var_list)

#         if product_variation in ext_var_list:
#             # increment the cart item quantity
#             index = ext_var_list.index(product_variation)
#             item_id = id[index]
#             item = CartItem.objects.get(product=product, id=item_id)
#             item.quantity += 1
#             item.save()
#         else:
#            # create new cart item
#            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
#            if len(product_variation) > 0:
#                 item.variations.clear()
#                 item.variations.add(*product_variation)
#             item.save()    
#     else:
#         cart_item = CartItem.objects.create(
#             product = product,
#             quantity = 1,
#             cart = cart,
#         )
#         if len(product_variation) > 0:
#             cart_item.variations.clear()
#             cart_item.variations.add(item)
#         cart_item.save()
#     # return HttpResponse(cart_item.product)
#     # exit()
#     return redirect('cart')

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # get the product
    product_variation = []

    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)

        ext_var_list = []
        id = []
        for item in cart_item:
            existing_variation = item.variations.all()
            ext_var_list.append(list(existing_variation))
            id.append(item.id)
        print(ext_var_list)

        if product_variation in ext_var_list:
            index = ext_var_list.index(product_variation)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()
    else:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart') 


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')




def cart(request, total=0, quantity=0, cart_items=None):
    
    try:
        tax = 0  # define default value
        grand_total = 0  # define default value
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/ 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # just ignore
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    # print(context['cart_items'])
    return render(request, 'store/cart.html', context)