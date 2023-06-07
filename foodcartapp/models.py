from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        db_index=True,

    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        db_index=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50,
        db_index=True,
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=300,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(models.QuerySet):
    def with_price(self):
        return self.annotate(order_cost=Sum(F('products__product__price') * F('products__quantity')))


class Order(models.Model):
    RAW = 'RW'
    PROCESSED = 'PR'
    DELIVERY = 'DE'
    COMPLETE = 'CO'
    STATUS_CHOICES = [
        (RAW, 'Необработанный'),
        (PROCESSED, 'В ресторане'),
        (DELIVERY, 'В доставке'),
        (COMPLETE, 'Завершен')
    ]

    firstname = models.CharField(
        'имя',
        max_length=50,
        db_index=True,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        db_index=True,
    )
    address = models.CharField(
        'адрес доставки',
        max_length=200,
        db_index=True,
    )
    status = models.CharField(
        'Статус заказа',
        max_length=2,
        choices=STATUS_CHOICES,
        default=RAW,
        db_index=True,
    )

    comment = models.TextField(
        'Комментарий к заказу',
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id} {self.firstname} {self.lastname} {self.phonenumber}'


class ProductInOrder(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='products',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='orders',
        on_delete=models.DO_NOTHING
    )
    quantity = models.PositiveIntegerField(
        'количество',
        validators=[MinValueValidator(0)]
    )
    fixed_price = models.DecimalField(
        'фиксированная стоимость',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    def __str__(self):
        return self.product.name
