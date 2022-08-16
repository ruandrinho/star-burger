import json
from django.http import JsonResponse
from django.templatetags.static import static


from .models import Product
from .models import Order
from .models import OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        order_from_site = json.loads(request.body.decode())
    except ValueError:
        return JsonResponse({'status': 'error'})
    if order_from_site['firstname'] and order_from_site['phonenumber'] and order_from_site['address']\
            and order_from_site['products']:
        order = Order.objects.create(
            first_name=order_from_site['firstname'],
            last_name=order_from_site['lastname'],
            phone_number=order_from_site['phonenumber'],
            address=order_from_site['address'],
        )
        for order_item in order_from_site['products']:
            if order_item['product'] and order_item['quantity']:
                product = Product.objects.get(id=order_item['product'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=order_item['quantity']
                )
    return JsonResponse({'status': 'ok'})
