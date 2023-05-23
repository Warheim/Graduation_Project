from django.db import models
from django.contrib.auth.models import AbstractUser
from orders.settings import USER_TYPE_CHOICES


class User(AbstractUser):
    pass


class Shop(models.Model):
    pass


class Category(models.Model):
    pass


class Product(models.Model):
    pass


class ProductInfo(models.Model):
    pass


class Parameter(models.Model):
    pass


class ProductParameter(models.Model):
    pass


class Order(models.Model):
    pass


class OrderProduct(models.Model):
    pass


class Buyer(models.Model):
    pass
