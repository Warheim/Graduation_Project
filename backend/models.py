from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from orders.settings import USER_TYPE_CHOICES


class User(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    type = models.CharField(max_length=30, verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, default='buyer')
    company = models.CharField(max_length=50, verbose_name='Компания')
    position = models.CharField(max_length=50, verbose_name='Должность')
    is_active = models.BooleanField(verbose_name='Активен', default=True)

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'company', 'position']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)


class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(blank=True)
    address = models.CharField(max_length=150, blank=True)
    order_accept_status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('name',)


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='Категория', unique=True)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('name',)


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Товар')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Список товаров'
        ordering = ('name',)


class ProductInfo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shops')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    model = models.CharField(max_length=20, verbose_name='Модель', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество на складе')
    price = models.DecimalField(decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(decimal_places=2, verbose_name='Рекомендуемая розничная цена')

    def __str__(self):
        return f'{self.product.name} в магазине {self.shop.name}'

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Реестр информации о товарах'
        ordering = ('name',)


class Parameter(models.Model):
    name = ''


class ProductParameter(models.Model):
    product_info = ''
    parameter = ''
    quantity = ''


class Buyer(models.Model):
    user = ''
    phone = ''
    address = ''


class Order(models.Model):
    buyer = ''
    date_time = ''
    status = ''


class OrderProduct(models.Model):
    order = ''
    product_info = ''
    quantity = ''
