from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
import phonenumbers


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
        return Response({'error': 'query has no products'})
    if type(order_from_site['products']) is not list:
        return Response({'error': 'products are not list'})
    if not len(order_from_site['products']):
        return Response({'error': 'products list could not be empty'})
    for argument in ['firstname', 'lastname', 'phonenumber', 'address']:
        if argument not in order_from_site:
            return Response({'error': f'query has no {argument}'})
        if type(order_from_site[argument]) is not str:
            return Response({'error': f'{argument} is not string'})
        if not len(order_from_site[argument]):
            return Response({'error': f'{argument} could not be empty'})
    parsed_phonenumber = phonenumbers.parse(order_from_site['phonenumber'], 'RU')
    if not phonenumbers.is_possible_number(parsed_phonenumber):
        return Response({'error': 'phonenumber is not possible'})
    if not phonenumbers.is_valid_number(parsed_phonenumber):
        return Response({'error': 'phonenumber is not valid'})
    order = Order.objects.create(
        first_name=order_from_site['firstname'],
        last_name=order_from_site['lastname'],
        phone_number=order_from_site['phonenumber'],
        address=order_from_site['address'],
    )
    for order_item in order_from_site['products']:
        if 'product' not in order_item:
            continue
        if 'quantity' not in order_item:
            continue
        try:
            product = Product.objects.get(id=order_item['product'])
        except Product.DoesNotExist:
            order.delete()
            return Response({'error': 'invalid id of product'})
        except Product.MultipleObjectsReturned:
            order.delete()
            return Response({'error': 'invalid id of product'})
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=order_item['quantity']
        )
    return Response({'status': 'ok'})
