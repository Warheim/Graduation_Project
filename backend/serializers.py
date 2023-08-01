from rest_framework import serializers

from backend.models import (Customer, Provider, Category,
                            Characteristic, Order, OrderItem,
                            Product, ProductCharacteristic,
                            Catalog, User, CustomerInfo, Shop)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize user instances
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "username",
            "company",
            "position",
            "type",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["is_staff", "is_superuser"]


class ProviderSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize supplier instances
    """

    url = serializers.CharField(required=False)
    order_is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Provider
        fields = ["id", "user", "name", "url", "order_is_active"]


class CustomerInfoSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize customer info instances
    """

    class Meta:
        model = CustomerInfo
        fields = ['id', 'customer_id', 'city', 'street', 'house',
                  'structure', 'building', 'apartment', 'phone', ]


class ShopSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize customer shop instances
    """

    class Meta:
        model = Shop
        fields = ["id", "name"]


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize customer instances
    """

    customer_info = CustomerInfoSerializer(read_only=True, many=True)
    shop = ShopSerializer(read_only=True, many=True)

    class Meta:
        model = Customer
        fields = ["id", "user", "name", "customer_info", "shop"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize category instances
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize product instances
    """

    class Meta:
        model = Product
        fields = ["id", "name", "category_id"]


class CharacteristicSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize characteristic instances
    """

    class Meta:
        model = Characteristic
        fields = ["id", "name"]


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize product characteristic instances
    """

    class Meta:
        model = ProductCharacteristic
        fields = ["id", "catalog_id", "characteristic_id", "value"]


class CatalogSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize catalog instances
    """

    product_characteristics = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Catalog
        fields = [
            "id",
            "provider_id",
            "product_id",
            "article",
            "purchase_price",
            "retail_price",
            "quantity",
            "delivery_cost",
            "product_characteristics",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize order position instances
    """

    catalog = CatalogSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order_id",
            "catalog_id",
            "quantity",
            "catalog",
        ]
        read_only_fields = ["order_id", "catalog_id", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize order instances
    """

    order_items = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_id",
            "order_date",
            "customer_info",
            "total_quantity",
            "total_price",
            "order_status",
            "delivery_info",
            "order_items",
        ]
        read_only_fields = [
            "order_date",
            "total_quantity",
            "total_price",
            "order_status",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize order instances upon create or update actions
    """

    class Meta:
        model = Order
        fields = ["id", "customer", "order_date", "delivery_info", "order_status"]
        read_only_fields = ["order_date", "order_status"]
