import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Product, Order, ProductInOrder


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
    try:
        order_raw = request.data
        if not isinstance(order_raw['firstname'], str):
            raise ValueError('firstname')
        if not isinstance(order_raw['lastname'], str):
            raise ValueError('lastname')
        if not isinstance(order_raw['address'], str):
            raise ValueError('address')
        if not order_raw['phonenumber']:
            raise KeyError('phonenumber')
        if isinstance(order_raw['products'], list) and not order_raw['products']:
            raise KeyError('products')

        phone = PhoneNumber.from_string(order_raw['phonenumber'], region='RU')
        if not phone.is_valid():
            raise ValueError('phonenumber')

        order = Order.objects.create(
            firstname=order_raw['firstname'],
            lastname=order_raw['lastname'],
            contact_phone=order_raw['phonenumber'],
            address=order_raw['address'],
        )

        for prod in order_raw['products']:
            product = Product.objects.get(id=prod['product'])
            ProductInOrder.objects.create(
                order=order,
                product=product,
                quantity=prod['quantity'],
            )
    except IntegrityError as integrity:
        return Response({
            'error': f'{integrity} error'
        }, status=400)
    except ObjectDoesNotExist as error:
        return Response({
            'error': f'{error}'
        }, status=400)
    except TypeError:
        return Response({
            'error': 'products are not list'
        }, status=400)
    except KeyError as key:
        return Response({
            'error': f'missing {key} value'
        }, status=400)
    except ValueError as value:
        return Response({
            'error': f'wrong {value} value',
        }, status=400)

    return Response({})
