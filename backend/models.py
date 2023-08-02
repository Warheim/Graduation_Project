import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator
from django.db import models
from orders.settings import USER_TYPE_CHOICES, STATE_CHOICES


class User(AbstractUser):
    """
    Class to describe custom user
    """

    email = models.EmailField()
    password = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    company = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default='customer'
    )
    is_active = models.BooleanField(default=True)
    first_name = None
    last_name = None

    objects = UserManager()

    REQUIRED_FIELDS = ['email', 'company', 'position']

    def __str__(self):
        return f'{self.username} {self.email}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('id',)


class Provider(models.Model):
    """
    Class to describe products providers
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=200, null=True, blank=True)
    order_is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Список поставщиков'
        ordering = ('-order_is_active', 'name')

    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    Class to describe shop's in which customer is working
    """

    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    Class to describe products customer
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    shop = models.ManyToManyField(Provider, related_name='customers', blank=False)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Список покупателей'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Class to describe products categories
    """

    name = models.CharField(max_length=30, unique=True)
    provider_id = models.ManyToManyField(Provider, related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Class to describe products
    """

    name = models.CharField(max_length=50)
    category_id = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Catalog(models.Model):
    """
    Class to describe catalog of products and its provider
    """

    provider_id = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name='catalogs'
    )
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='catalogs'
    )
    article = models.CharField(max_length=50, null=True, blank=True)
    purchase_price = models.DecimalField(
        decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)]
    )
    retail_price = models.DecimalField(
        decimal_places=2, max_digits=16, validators=[MinValueValidator(0.01)]
    )
    quantity = models.PositiveIntegerField()
    delivery_cost = models.PositiveIntegerField(validators=[MinValueValidator(0)], default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Каталог продуктов'
        verbose_name_plural = 'Список продуктов каталога'
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'product_id', 'provider_id'], name='unique_catalog'
            ),
        ]
        ordering = ('product_id', 'purchase_price')

    def __str__(self):
        return f'Продукт {self.product_id.name} у {self.provider_id.name}'


class Characteristic(models.Model):
    """
    Class to describe products characteristics
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Список характеристик'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductCharacteristic(models.Model):
    """
    Class to describe some characteristic of product in catalog
    """

    catalog_id = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name='product_characteristics'
    )
    characteristic_id = models.ForeignKey(
        Characteristic, on_delete=models.CASCADE, related_name='product_characteristics'
    )
    value = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Характеристика продукта в каталоге'
        verbose_name_plural = 'Список характеристик продукта в каталоге'
        constraints = [
            models.UniqueConstraint(
                fields=['catalog_id', 'characteristic_id'], name='unique_product_characteristic'
            ),
        ]
        ordering = ('catalog_id', 'value')

    def __str__(self):
        return self.value


class CustomerInfo(models.Model):
    """
    Class to describe customer info for delivery
    """
    customer_id = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='cart_positions',
    )
    city = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    house = models.CharField(max_length=50, null=True, blank=True)
    structure = models.CharField(max_length=50, null=True, blank=True)
    building = models.CharField(max_length=50, null=True, blank=True)
    apartment = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)


class Order(models.Model):
    """
    Class to describe order
    """

    customer_id = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders'
    )
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=15, choices=STATE_CHOICES, default='saved')
    delivery_info = models.ForeignKey(
        CustomerInfo, on_delete=models.CASCADE, related_name='orders'
    )

    def sum_total_quantity(self):
        """
        Calculates total quantity of items in order
        :return: total quantity of items
        """

        return sum([position.quantity for position in self.order_items.all()])

    @property
    def total_quantity(self) -> int:
        """
        Sets total_quantity field of order instance
        :return: total quantity of items
        """
        return self.sum_total_quantity()

    def sum_total_price(self):
        """
        Calculates total price of items in order
        :return: total price of items
        """
        return sum([position.purchase_price for position in self.order_items.all()])

    @property
    def total_price(self) -> int:
        """
        Sets total_price field of order instance
        :return: total price of items
        """
        return self.sum_total_price()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-order_date', 'customer_id')

    def __str__(self):
        return f'{self.customer_id.name} {self.order_date}'


class OrderItem(models.Model):
    """
    Class to describe product position of some order
    """

    order_id = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items'
    )
    catalog_id = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name='order_items'
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Список позиций заказов'
        constraints = [
            models.UniqueConstraint(
                fields=['order_id', 'catalog_id'], name='unique_order_catalog'
            ),
        ]
        ordering = ('order_id', 'quantity')


class PasswordResetToken(models.Model):
    """
    Class to describe password reset token
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4)

    class Meta:
        verbose_name = 'Токен сброса пароля'
        verbose_name_plural = 'Токены сброса пароля'

    def __str__(self):
        return f'Password reset token for user {self.user}'
