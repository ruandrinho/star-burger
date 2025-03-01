from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.conf import settings
from geopy import distance
from geocache.views import fetch_coordinates
import requests


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from geocache.models import Place


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
        return render(request, "login.html", context={
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

        return render(request, "login.html", context={
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

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    unready_orders = Order.objects.with_total_cost().exclude(status=3).order_by('status').with_possible_restaurants()
    restaurants = Restaurant.objects.all()

    addresses = [restaurant.address for restaurant in restaurants]
    addresses.extend([order.address for order in unready_orders])
    places_by_address = {}
    for place in Place.objects.filter(address__in=addresses):
        places_by_address[place.address] = place

    for restaurant in restaurants:
        if restaurant.address in places_by_address:
            continue
        restaurant_place = Place.objects.create(address=restaurant.address)
        try:
            restaurant_coordinates = fetch_coordinates(
                settings.YANDEX_GEOCODER_API_KEY,
                restaurant.address
            )
        except requests.exceptions.RequestException:
            restaurant_coordinates = None
        if restaurant_coordinates:
            restaurant_place.longitude, restaurant_place.latitude = restaurant_coordinates
            restaurant_place.save()
        places_by_address[restaurant.address] = restaurant_place

    for order in unready_orders:
        if order.assigned_restaurant:
            continue
        if order.address in places_by_address:
            order_place = places_by_address[order.address]
        else:
            order_place = Place.objects.create(address=order.address)
            try:
                order_coordinates = fetch_coordinates(settings.YANDEX_GEOCODER_API_KEY, order.address)
            except requests.exceptions.RequestException:
                order_coordinates = None
            if order_coordinates:
                order_place.longitude, order_place.latitude = order_coordinates
                order_place.save()
            places_by_address[order.address] = order_place
        if not order_place.longitude or not order_place.latitude:
            continue
        order_lat_and_lon = (order_place.latitude, order_place.longitude)
        for restaurant in order.possible_restaurants:
            restaurant_place = places_by_address[restaurant.address]
            if restaurant_place.longitude and restaurant_place.latitude:
                restaurant_lat_and_lon = (restaurant_place.latitude, restaurant_place.longitude)
                restaurant.distance = distance.distance(order_lat_and_lon, restaurant_lat_and_lon).km
        order.possible_restaurants = [
            {'name': restaurant.name, 'distance': restaurant.distance} for restaurant in order.possible_restaurants
        ]

    return render(request, template_name='order_items.html', context={
        'order_items': unready_orders
    })
