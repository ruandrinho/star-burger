from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
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
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
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
        max_length=200,
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
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderManager(models.Manager):

    def with_total_cost(self):
        return self.annotate(
            total_cost=models.Sum(
                models.F('items__price') * models.F('items__quantity')
            )
        )


class Order(models.Model):
    NEW_STATUS, COOKING_STATUS, DELIVERING_STATUS, COMPLETE_STATUS = range(4)
    CASH_PAYMENT, CARD_PAYMENT = range(2)
    status = models.IntegerField(
        'статус',
        choices=[
            (NEW_STATUS, 'Необработанный'),
            (COOKING_STATUS, 'Готовится'),
            (DELIVERING_STATUS, 'В доставке'),
            (COMPLETE_STATUS, 'Завершён'),
        ],
        default=NEW_STATUS,
        db_index=True
    )
    assigned_restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="назначенный ресторан",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    payment = models.IntegerField(
        'способ оплаты',
        choices=[
            (CASH_PAYMENT, 'Наличностью'),
            (CARD_PAYMENT, 'Электронно'),
        ],
        db_index=True
    )
    firstname = models.CharField(
        'имя',
        max_length=50,
        db_index=True
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True
    )
    phonenumber = PhoneNumberField(
        'телефон',
        db_index=True
    )
    address = models.TextField(
        'адрес',
        max_length=200,
        db_index=True
    )
    comment = models.TextField(
        'комментарий',
        blank=True
    )
    created_at = models.DateTimeField(
        'создан',
        auto_now_add=True,
        db_index=True
    )
    called_at = models.DateTimeField(
        'позвонили клиенту',
        null=True,
        blank=True,
        db_index=True
    )
    delivered_at = models.DateTimeField(
        'доставили клиенту',
        null=True,
        blank=True,
        db_index=True
    )
    objects = OrderManager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.address})"

    def save_model(self, request, obj, form, change):
        if obj.status == obj.NEW_STATUS and obj.assigned_restaurant:
            obj.status = obj.COOKING_STATUS
        super().save_model(request, obj, form, change)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name="заказ",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.IntegerField(
        'количество',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'пункт заказа'
        verbose_name_plural = 'пункты заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"{self.order.firstname} ({self.order.address}) - {self.product.name} ({self.quantity})"
