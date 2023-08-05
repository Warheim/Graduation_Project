from uuid import UUID

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.db.models.query import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from celery.result import AsyncResult

from orders.celery import app as celery_app
from backend.tasks import send_email, do_import
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


class UserViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with user instances
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["post", "patch", "get", "delete"]

    def get_queryset(self):
        """
        Get the list of user items for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(id=self.request.user.id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "destroy":
            return [IsAdmin()]
        if self.action in ["retrieve", "update", "partial_update"]:
            retrieve_update_permission = IsAdmin | IsUser
            return [retrieve_update_permission()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Create a user instance and send email confirmation.
        """

        if not request.data.get("password"):
            return Response(
                {"password": ["This field is required."]}, status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(request.data["password"])
        except Exception as errors:
            return Response(
                {"error": [error for error in errors]}, status.HTTP_400_BAD_REQUEST
            )

        request.data["password"] = make_password(request.data["password"])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        """
        Destroy (deactivate) a user instance.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Update a user instance.
        """

        if "type" in request.data:
            return Response(
                {"error": "type cannot be amended"}, status=status.HTTP_403_FORBIDDEN
            )

        password = request.data.pop("password", None)

        if (
                password
                and request.data.get("new_password")
                and request.user == self.get_object()
        ):
            if check_password(password, self.get_object().password):
                try:
                    validate_password(request.data["new_password"])
                except Exception as errors:
                    return Response(
                        {"error": [error for error in errors]},
                        status.HTTP_400_BAD_REQUEST,
                    )
                request.data["password"] = make_password(request.data["new_password"])

            else:
                return Response(
                    {"error": "wrong password"}, status=status.HTTP_403_FORBIDDEN
                )

        if type(request.data.get("is_superuser")) == bool and request.user.is_superuser:
            instance = self.get_object()
            instance.is_superuser = request.data.get("is_superuser")
            instance.save()

        if type(request.data.get("is_staff")) == bool and request.user.is_superuser:
            instance = self.get_object()
            instance.is_staff = request.data.get("is_staff")
            instance.save()

        return super().update(request, *args, **kwargs)


class PasswordResetView(APIView):
    """
    APIView class to perform password reset operations
    """

    def post(self, request):
        """
        Method to arrange receipt of password reset token and to reset password using this token
        :param request: request objects
        :return: response with corresponding status code
        """

        if request.data.get("token"):
            if {"username", "new_password"}.issubset(request.data):
                if not User.objects.filter(
                        username=request.data.get("username")
                ).exists():
                    return Response(
                        {"error": "User with such username does not exist"},
                        status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.get(username=request.data.get("username"))

                try:
                    UUID(request.data.get("token"))
                except ValueError:
                    return Response(
                        {"error": "Wrong token"}, status.HTTP_400_BAD_REQUEST
                    )

                if not PasswordResetToken.objects.filter(
                        token=request.data.get("token")
                ).exists():
                    return Response(
                        {"error": "Wrong token"}, status.HTTP_400_BAD_REQUEST
                    )

                token = PasswordResetToken.objects.get(token=request.data.get("token"))

                if token.user == user:
                    try:
                        validate_password(request.data["new_password"])
                    except Exception as errors:
                        return Response(
                            {"error": [error for error in errors]},
                            status.HTTP_400_BAD_REQUEST,
                        )
                    token.delete()

                    user.password = make_password(request.data.get("new_password"))
                    user.save()
                    return Response(
                        {"success": "Your password has been changed"},
                        status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Wrong token"}, status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response(
                    {
                        "error": '"username" and "new_password" fields are required for set of new password'
                    },
                    status.HTTP_400_BAD_REQUEST,
                )
        else:
            if request.data.get("username"):
                if not User.objects.filter(
                        username=request.data.get("username")
                ).exists():
                    return Response(
                        {"error": "User with such username does not exist"},
                        status.HTTP_400_BAD_REQUEST,
                    )

                user = User.objects.get(username=request.data.get("username"))

                token, created = PasswordResetToken.objects.get_or_create(user=user)

                text = f"Your password reset token is {token.token}"
                send_email.delay("Password reset token", text, user.email)
                return Response(
                    {
                        "success": "Reset token is sent to your email."
                    },
                    status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": '"username" field is required for reset token obtain'},
                    status.HTTP_400_BAD_REQUEST,
                )


class ProviderViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with provider instances
    """
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    http_method_names = ["post", "patch", "get", "delete"]

    def get_queryset(self):
        """
        Get the list of provider items for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser or self.request.user.type == "customer":
            return queryset
        if self.request.user.type == "provider":
            return queryset.filter(user=self.request.user.id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "destroy":
            return [IsAdmin()]
        if self.action == "retrieve":
            retrieve_permission = IsAdmin | IsOwner | IsCustomer
            return [retrieve_permission()]
        if self.action in ["update", "partial_update"]:
            return [IsOwner()]
        if self.action == "create":
            return [IsProvider()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Create a provider instance.
        """

        request.data["user"] = request.user.id
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy (stop orders for) a provider instance.
        """

        instance = self.get_object()
        instance.order_status = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Update a provider instance.
        """

        if "user" in request.data:
            return Response(
                {"error": "user cannot be updated"}, status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class CategoryViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with category instances
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["post", "patch", "get", "delete"]

    filterset_fields = ["id", "name"]
    search_fields = ["name"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "create":
            create_permission = IsAdmin | IsProvider
            return [create_permission()]
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsAdmin()]
        return []


class ProductViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with product instances
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["post", "patch", "get", "delete"]
    filterset_fields = ["id", "name", "category__id", "category__name"]
    search_fields = ["name"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "create":
            create_permission = IsAdmin | IsProvider
            return [create_permission()]
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsAdmin()]
        return []


class CharacteristicViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with characteristic instances
    """
    queryset = Characteristic.objects.all()
    serializer_class = CharacteristicSerializer
    http_method_names = ["post", "patch", "get", "delete"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "create":
            create_permission = IsAdmin | IsProvider
            return [create_permission()]
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsAdmin()]
        return []


class CatalogViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with catalog instances
    """
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    http_method_names = ["post", "patch", "get", "delete"]
    filterset_fields = [
        "product_id__id",
        "product_id__name",
        "product_id__category_id__id",
        "product_id__category_id__name",
        "provider_id__id",
        "provider_id__name",
    ]
    search_fields = [
        "article",
        "product_id__name",
        "product_id__category_id__name",
        "provider_id__name",
        "provider_id__url",
        "product_characteristics__value",
    ]

    def get_queryset(self):
        """
        Get the list of catalog items for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser:
            return queryset.select_related("product_id").prefetch_related(
                "product_characteristics", "product"
            )
        if self.request.user.type == "customer":
            return (
                queryset.filter(provider_id__order_is_active=True, quantity__gt=0)
                .select_related("product_id")
                .prefetch_related("product_characteristics", "product")
            )
        if self.request.user.type == "provider":
            return (
                queryset.filter(provider_id__user=self.request.user)
                .select_related("product_id")
                .prefetch_related("product_characteristics", "product")
            )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list"]:
            return [IsAuthenticated()]
        if self.action in ["retrieve"]:
            retrieve_permission = IsAdmin | IsCustomer | IsCatalogOwner
            return [retrieve_permission()]
        if self.action == "create":
            return [IsProvider()]
        if self.action in ["update", "partial_update"]:
            return [IsCatalogOwner()]
        if self.action == "destroy":
            return [IsAdmin()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Create a catalog instance.
        """

        user = request.user
        if not Provider.objects.filter(user=user).exists():
            return Response(
                {
                    "error": "you need to create provider before you create or update catalog"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["provider"] = Provider.objects.get(user=user).id
        if Catalog.objects.filter(
                article=request.data.get("article"),
                product_id=request.data.get("product_id"),
                provider_id=request.data.get("provider_id"),
        ).exists():
            return Response(
                {"error": "This catalog already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Update a catalog instance.
        """

        if request.data.get("product_id") or request.data.get("provider_id"):
            return Response(
                {"error": "Catalog product and provider cannot be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        catalog = self.get_object()
        if request.data.get("article"):
            if Catalog.objects.filter(
                    article=request.data.get("article"),
                    product=catalog.product_id.id,
                    supplier=catalog.provider_id.id,
            ).exists():
                return Response(
                    {"error": "Catalog with this article and product already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().update(request, *args, **kwargs)


class ProductCharacteristicViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with product characteristic instances
    """
    queryset = ProductCharacteristic.objects.all()
    serializer_class = ProductCharacteristicSerializer
    http_method_names = ["post", "patch", "get", "delete"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsProvider()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsCatalogReferencedOwner()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Create a product characteristic instance.
        """

        if (
                request.data.get("catalog_id")
                and Catalog.objects.filter(id=request.data.get("catalog_id")).exists()
        ):
            if (
                    Catalog.objects.get(id=request.data.get("catalog_id")).provider_id.user
                    == request.user
            ):
                if ProductCharacteristic.objects.filter(
                        catalog_id=request.data.get("catalog_id"),
                        characteristic_id=request.data.get("characteristic_id"),
                ).exists():
                    return Response(
                        {"error": "this catalog already has this characteristic"},
                        status.HTTP_400_BAD_REQUEST,
                    )
                return super().create(request, *args, **kwargs)
            else:
                return Response(
                    {"detail": "You do not have permission to perform this action."},
                    status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {
                    "error": '"catalog_id" is either not indicated or such catalog does not exist'
                },
                status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        """
        Update a product characteristic instance.
        """

        if request.data.get("catalog_id") or request.data.get("characteristic_id"):
            return Response(
                {"error": 'Only "value" field can be updated'},
                status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)


class ImportView(APIView):
    """
    APIView class to perform catalog import operations
    """

    def post(self, request):
        """
        Method to arrange import of catalogs from providers file with determinated structure
        :param request: request object
        :return: response with corresponding status code
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status.HTTP_401_UNAUTHORIZED,
            )
        if not request.user.type == "provider":
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status.HTTP_403_FORBIDDEN,
            )
        url = request.data.get("url")
        if url:
            async_result = do_import.delay(url, request.user.id)
            return Response({"detail": f"Your task id is {async_result.task_id}"}, status.HTTP_200_OK)
        return Response({"url": ["This field is required."]}, status.HTTP_400_BAD_REQUEST)


class ImportCheckView(APIView):
    """
    APIView class to get result of catalog import operations
    """

    def get(self, request, task_id):
        """
        Checks status and result of celery-task fulfilment for authenticated supplier or admin user
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status.HTTP_401_UNAUTHORIZED,
            )
        if not request.user.type == "provider" and not request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status.HTTP_403_FORBIDDEN,
            )
        result = AsyncResult(task_id, app=celery_app)
        return Response({"status": result.status, 'result': result.result}, status.HTTP_200_OK)


class CustomerViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with customer instances
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    http_method_names = ["patch", "get"]

    def get_queryset(self):
        """
        Get the list of customers for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser:
            return queryset.prefetch_related("orders")
        if self.request.user.type == "customer":
            return queryset.filter(user=self.request.user.id).prefetch_related(
                "orders"
            )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action in ["list"]:
            list_permission = IsAdmin | IsCustomer
            return [list_permission()]
        if self.action in ["retrieve"]:
            retrieve_permission = IsAdmin | IsOwner
            return [retrieve_permission()]
        if self.action in ["update", "partial_update"]:
            return [IsOwner()]
        if self.action == "create":
            return [IsCustomer()]
        return []

    def update(self, request, *args, **kwargs):
        """
        Update a purchaser instance.
        """

        if "user" in request.data:
            return Response(
                {"error": "user cannot be updated"}, status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with order instances
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ["post", "patch", "get", "delete"]

    def get_queryset(self):
        """
        Get the list of order items for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser:
            return queryset.select_related("order").prefetch_related(
                "order_items",
                "order_items__catalog_id",
                "order_items__catalog_id__product_characteristics",
            )
        if self.request.user.type == "customer":
            return (
                queryset.filter(customer__user=self.request.user)
                .select_related("order")
                .prefetch_related(
                    "order_items",
                    "order_items__catalog_id",
                    "order_items__catalog_id__product_characteristics",
                )
            )
        if self.request.user.type == "provider":
            return (
                queryset.filter(
                    order_items__catalog_id__provider_id__user=self.request.user
                )
                .distinct()
                .select_related("order")
                .prefetch_related(
                    "order_items",
                    "order_items__catalog_id",
                    "order_items__catalog_id__product_characteristics",
                )
            )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            retrieve_permission = IsAdmin | IsCustomerOwner | IsOrderCatalogOwner | IsOrderOwner
            return [retrieve_permission()]
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsCustomerOwner()]
        if self.action == "create":
            return [IsCustomer()]
        return []

    def create(self, request, *args, **kwargs):
        """
        Create an order instance and order position instances based on shopping cart instance and cart position
        instances
        """

        user = request.user
        if not Customer.objects.filter(user=user).exists():
            return Response(
                {
                    "error": "you need to create customer before you create or update orders"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        customer = Customer.objects.get(user=user)
        orders = customer.orders.all()
        if not orders.count():
            return Response(
                {"error": "Your orders is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["customer"] = customer.id

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if (
                Order.objects.get(id=request.data["order"]).customer_id
                != customer
        ):
            return Response(
                {"error": "Your can order delivery only to your shop"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        order = Order.objects.get(id=serializer.data["id"])
        providers = {}
        for position in orders:
            new_position = OrderItem.objects.create(
                order_id=order,
                catalog_id=position.catalog_id,
                quantity=position.quantity,
            )
            if new_position.catalog_id.provider_id.user not in providers:
                providers[new_position.catalog_id.provider_id.user] = [
                    {
                        "id": new_position.id,
                        "order_id": order.id,
                        "catalog_id": new_position.stock,
                        "quantity": new_position.quantity,
                    }
                ]
            else:
                providers[new_position.catalog_id.provider_id.user].append(
                    {
                        "id": new_position.id,
                        "order_id": order.id,
                        "catalog_id": new_position.stock,
                        "quantity": new_position.quantity,
                    }
                )

        for provider, items in providers.items():
            text = "You have new orders\n"
            for position in items:
                text += f'''Order #{position["order"]}, stock {position["stock"].product.name}, 
                quantity {position["quantity"]}, price {position["price"]}\n'''
            text += "Use application to confirm orders"
            send_email.delay("New order", text, provider.email)

        response = serializer.data.copy()
        response["total_quantity"] = order.total_quantity
        response["total_amount"] = order.total_amount
        send_email.delay(
            "New order",
            f"""Thank you for your order.
            You have created new order #{response["id"]} to store {response["shop"]} 
            for total amount of {response["total_amount"]}
            Status of your order will automatically update after suppliers confirmations""",
            user.email
        )
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        """
        Set to cancelled an order instance.
        """

        instance = self.get_object()

        if instance.order_status == "cancelled":
            return Response(
                {"error": "Order is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.order_status == "dellivered":
            return Response(
                {"error": "Dellivered order can`t be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.order_status = "cancelled"
        instance.save()

        for position in instance.order_items.all():
            catalog = Catalog.objects.get(id=position.catalog_id.id)
            catalog.quantity += position.quantity
            catalog.save()
        return Response({"success": "Order cancelled"}, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """
        Update an order instance.
        """

        instance = self.get_object()
        if instance.order_status == "cancelled":
            return Response(
                {"error": "Can`t update cancelled order"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if instance.order_status == "dellivered":
            return Response(
                {"error": "Dellivered order can`t be updated"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "customer" in request.data:
            return Response(
                {"error": "Customer cannot be updated"},
                status=status.HTTP_403_FORBIDDEN,
            )

        partial = kwargs.pop("partial", False)

        serializer = OrderCreateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class OrderItemViewSet(ModelViewSet):
    """
    ViewSet class to provide CRUD operations with order position instances
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    http_method_names = ["patch", "get"]
    filterset_fields = ["order__order_status", ]

    def get_queryset(self):
        """
        Get the list of order position items for view.
        """

        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        if self.request.user.is_superuser:
            return queryset.select_related("catalog").prefetch_related(
                "catalog__product_characteristics"
            )
        if self.request.user.type == "customer":
            return (
                queryset.filter(order__customer_id__user=self.request.user)
                .select_related("catalog")
                .prefetch_related("catalog__product_characteristics")
            )
        if self.request.user.type == "provider":
            return (
                queryset.filter(catalog__provider_id__user=self.request.user)
                .select_related("catalog")
                .prefetch_related("catalog__product_characteristics")
            )

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            retrieve_permission = IsAdmin | IsOrderItemOwner | IsCatalogReferencedOwner
            return [retrieve_permission()]
        if self.action in ["update", "partial_update"]:
            return [IsCatalogReferencedOwner()]
        return []
