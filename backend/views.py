from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from requests import get
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader

from backend.models import (Customer, Provider, Category,
                            Characteristic, Order, OrderItem,
                            Product, ProductCharacteristic,
                            Catalog, User, CustomerInfo, Shop,
                            PasswordResetToken)
from backend.permissions import (IsAdmin, IsProvider, IsUser,
                                 IsCustomer, IsOwner,
                                 IsOrderOwner, IsOrderItemOwner,
                                 IsCustomerOwner, IsCatalogOwner,
                                 IsCatalogReferencedOwner, IsOrderCatalogOwner)
from backend.serializers import (CustomerSerializer, UserSerializer,
                                 ProviderSerializer, OrderSerializer,
                                 CategorySerializer,
                                 CharacteristicSerializer,
                                 OrderCreateSerializer,
                                 OrderItemSerializer,
                                 ProductCharacteristicSerializer,
                                 ProductSerializer,
                                 CatalogSerializer)
