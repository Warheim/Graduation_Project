from django.db import models
from django.contrib.auth.models import AbstractUser
from orders.settings import USER_TYPE_CHOICES


class User(AbstractUser):
    first_name = ''
    last_name = ''
    email = ''
    type = ''
    company = ''
    position = ''


class Shop(models.Model):
    user = ''
    name = ''
    url = ''
    filename = ''
    address = ''
    order_accept_status = ''


class Category(models.Model):
    name = ''
    shops = ''


class Product(models.Model):
    name = ''
    category = ''


class ProductInfo(models.Model):
    shop = ''
    product = ''
    model = ''
    quantity = ''
    price = ''
    price_rrc = ''


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
