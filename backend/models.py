from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from orders.settings import USER_TYPE_CHOICES, STATE_CHOICES
import uuid

class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    type = models.CharField(max_length=30, verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, default='buyer')
    company = models.CharField(max_length=50, verbose_name='Компания')
    position = models.CharField(max_length=50, verbose_name='Должность')
    is_active = models.BooleanField(verbose_name='Активен', default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)


class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(blank=True, verbose_name='Ссылка')
    address = models.CharField(max_length=150, blank=True, verbose_name='Адрес')
    order_status = models.BooleanField(default=True, verbose_name='Статус заказа')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('name',)


class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name='Категория', unique=True)
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины', blank=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('name',)


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Товар')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Список товаров'
        ordering = ('name',)


class ProductInfo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_info', verbose_name='Магазин')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_info', verbose_name='Товар')
    model = models.CharField(max_length=20, verbose_name='Модель', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Цена')
    price_rrc = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Рекомендуемая розничная цена')

    def __str__(self):
        return f'{self.product.name} в магазине {self.shop.name}'

    class Meta:
        verbose_name = 'Информация о товаре'
        verbose_name_plural = 'Реестр информации о товарах'
        ordering = ('product',)


class Parameter(models.Model):
    name = models.CharField(max_length=20, verbose_name='Название')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Список названий параметров'
        ordering = ('name',)


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='parameters')
    value = models.CharField(max_length=50, verbose_name='Значение')

    def __str__(self):
        return f'{self.product_info.name} {self.parameter.name} {self.value}'

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='buyer')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=50, verbose_name='Адрес')

    def __str__(self):
        return f'{self.phone} {self.address}'

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Список покупателей'
        ordering = ('-address',)


class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время заказа')
    status = models.CharField(max_length=20, choices=STATE_CHOICES, verbose_name='Статус заказа')

    def __str__(self):
        return f'{self.date_time} {self.status}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-date_time',)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products', verbose_name='Заказ')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='order_products',
                                     verbose_name='Информация о товаре')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.product_info.name} {self.quantity}'

    class Meta:
        verbose_name = 'Товары в заказе'
        verbose_name_plural = 'Список товаров в заказах'


class PasswordResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4)

    class Meta:
        verbose_name = 'Токен сброса пароля'
        verbose_name_plural = 'Токены сброса пароля'

    def __str__(self):
        return f'Password reset token for user {self.user}'
