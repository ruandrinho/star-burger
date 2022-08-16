import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


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


@api_view(['POST'])
def register_order(request):
    order_from_site = request.data
    if 'products' not in order_from_site:
        return Response({'error': 'Query has no products'})
    if type(order_from_site['products']) is not list:
        return Response({'error': 'Products are not list'})
    if not len(order_from_site['products']):
        return Response({'error': 'Products list could not be empty'})
    if order_from_site['firstname'] and order_from_site['phonenumber'] and order_from_site['address']:
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
    return Response({'status': 'ok'})
