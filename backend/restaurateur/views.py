from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from geopy import distance
from backend.foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from backend.places.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "templates/login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "templates/login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="templates/products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="templates/restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_product_restaurants(restaurant_menu_products, order_products):
    product_restaurants = [
        rest_prod.restaurant for rest_prod in restaurant_menu_products
        if rest_prod.availability and rest_prod.product.id == order_products.product.id
    ]
    return product_restaurants


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects\
        .with_price()\
        .exclude(status='D')\
        .order_by('status')\
        .prefetch_related('cooking_restaurant', 'products', 'products__product', )

    restaurant_menu_products = RestaurantMenuItem.objects\
        .filter(availability=True) \
        .select_related('product', 'restaurant')

    places = Place.objects.filter(
        address__in=[order.address for order in orders] + [rest.address for rest in Restaurant.objects.all()]
    )
    places = {place.address: place for place in places}
    order_collections = []
    for order in orders:
        order.restaurants = set()
        restaurant_distance = []
        for prod in order.products.all():
            rest_product = get_product_restaurants(
                restaurant_menu_products,
                prod
            )
            if not order.restaurants:
                order.restaurants = set(rest_product)
                continue
            order.restaurants &= set(rest_product)

        delivery_place = places.get(order.address)
        delivery_coordinates = delivery_place.latitude, delivery_place.longitude
        print(delivery_coordinates)
        if None in delivery_coordinates:
            coordinates_error = True
        else:
            coordinates_error = False
            for restaurant in order.restaurants:
                restaurant_place = places.get(restaurant.address)
                restaurant_coordinates = restaurant_place.latitude, restaurant_place.longitude
                restaurant_dist = round(
                    distance.distance(restaurant_coordinates, delivery_coordinates).km, 2
                )
                restaurant_distance.append((restaurant.name, restaurant_dist))
            restaurant_distance.sort(key=lambda x: x[1])

        order_collection = {
            'id': order.id,
            'status': order.get_status_display(),
            'order_cost': order.order_cost,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
            'restaurants_distance': restaurant_distance,
            'coordinates_error': coordinates_error,
            'cooking_restaurant': order.cooking_restaurant,
        }
        order_collections.append(order_collection)
    return render(request, template_name='templates/order_items.html', context={
        'order_collections': order_collections,

    })
