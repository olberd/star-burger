from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError

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


def validate(data):
    errors = []
    if not isinstance(data['firstname'], str):
        errors.append(['не указано имя'])
    if not isinstance(data['lastname'], str):
        errors.append(['не указана фамилия'])
    if not isinstance(data['address'], str):
        errors.append(['не указан адрес'])
    if not data['phonenumber']:
        errors.append(['не указан номер телефона'])
    if isinstance(data['products'], list) and not data['products']:
        errors.append(['в заказе нет товаров'])
    if data['phonenumber'] and not PhoneNumber.from_string(data['phonenumber'], region='RU').is_valid():
        errors.append(['не правильный формат номера телефона'])
    if IntegrityError:
        errors.append(['integrity error'])
    if ObjectDoesNotExist:
        errors.append(['object does not exist'])

    if errors:
        raise ValidationError(errors)


@api_view(['POST'])
def register_order(request):
    order_raw = validate(request.data)

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

