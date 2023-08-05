from etc.admin import CustomModelPage
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models

from backend.models import User, Category, Product, Provider, Catalog, Characteristic, ProductCharacteristic, \
    Customer, OrderItem, Order
from backend.tasks import do_import

admin.site.site_header = 'Ordering Groceries Review Admin'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
        Class to ensure all admin options and functionality for User model.
    """

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": (('company', 'position'), 'type')}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    ("is_staff",
                    "is_superuser"),
                    "groups",
                ),
            },
        ),
        ("Important dates", {"fields": (("last_login", "date_joined"),)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", 'email',
                           ('company', 'position'),
                           'type'),
            },
        ),
    )
    list_display = ('id', "username", "email", "first_name", "last_name", 'company', 'position')
    list_filter = ('type', "is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email", 'company', 'position')
    readonly_fields = ('is_superuser', "last_login", "date_joined")

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def has_add_permission(self, request):
        """
        Return False since addition of new User instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of User instances is not allowed by the admin site.
        """
        return False


class CategoryProviderInline(admin.TabularInline):
    """
    Class for inline creation, view and editing of CategoryProvider instances.
    """

    model = Category.provider_id.through
    extra = 0

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of CategoryProvider instances is not allowed by the admin site.
        """
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Category model.
    """

    list_display = ('id', 'name',)
    search_fields = ('name',)
    inlines = [CategoryProviderInline, ]
    exclude = ('provider_id', )

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Category instances is not allowed by the admin site.
        """
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Product model.
    """

    list_display = ('id', 'name', 'category_id', 'description')
    list_filter = ('category_id', )
    search_fields = ('name', 'category_id')

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Product instances is not allowed by the admin site.
        """
        return False


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Provider model.
    """

    list_display = ('id', 'name', 'url', 'order_is_active', 'user')
    list_filter = ('order_is_active', )
    search_fields = ('name', 'url')
    inlines = [CategoryProviderInline, ]
    readonly_fields = ('user', )

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_add_permission(self, request):
        """
        Return False since addition of new Provider instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Provider instances is not allowed by the admin site.
        """
        return False


class ProductCharacteristicInline(admin.TabularInline):
    """
    Class for inline creation, view and editing of ProductCharacteristic instances.
    """
    model = ProductCharacteristic
    extra = 0


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Characteristic model.
    """

    list_display = ('id', 'name', )
    search_fields = ('name', )

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Characteristic instances is not allowed by the admin site.
        """
        return False


class OrderItemInline(admin.TabularInline):
    """
    Class for inline view and editing of OrderItem instances.
    """

    model = OrderItem
    extra = 0
    fields = ('order_id', 'catalog_id', 'quantity')
    readonly_fields = ('order_id',)

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order_id__order_status='saved', catalog_id__provider_id__user=request.user)

    def has_add_permission(self, request, obj):
        """
        Return False since addition of new OrderItem instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of OrderItem instances is not allowed by the admin site.
        """
        return False


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Catalog model.
    """

    list_display = ('id', 'article', 'product_id', 'provider_id', 'is_active', 'purchase_price', 'retail_price',
                    'quantity', 'delivery_cost')
    list_filter = ('product_id', 'provider_id')
    search_fields = ('article',)
    inlines = [ProductCharacteristicInline, OrderItemInline]
    readonly_fields = ('product_id', 'provider_id')

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(provider_id__user=request.user.id)

    def has_add_permission(self, request):
        """
        Return False since addition of new Catalog instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Catalog instances is not allowed by the admin site.
        """
        return False


class CustomerShopInline(admin.TabularInline):
    """
    Class for inline creation, view and editing of Shop instances.
    """
    model = Customer.shop.through
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Customer model.
    """

    list_display = ('id', 'name', 'user')
    search_fields = ('name',)
    inlines = [CustomerShopInline, ]
    readonly_fields = ('name', 'user')

    def has_add_permission(self, request):
        """
        Return False since addition of new Customer instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Customer instances is not allowed by the admin site.
        """
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for Order model.
    """

    fields = ('customer_id', 'order_date', 'order_status', 'delivery_info')
    list_display = ('customer_id', 'order_date', 'order_status', 'delivery_info')
    list_filter = ('customer_id', 'order_date', 'order_status')
    search_fields = ('customer_id', )

    readonly_fields = ('customer_id', 'order_date', 'order_status', 'delivery_info')
    inlines = [OrderItemInline, ]

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order_items__catalog_id__provider_id__user=request.user).distinct()

    def has_add_permission(self, request):
        """
        Return False since addition of new Order instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of Order instances is not allowed by the admin site.
        """
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
        Class to ensure all admin options and functionality for OrderPosition model.
    """

    fields = ('order_id', 'catalog_id', 'quantity')
    readonly_fields = ('order_id', 'catalog_id', 'quantity')
    list_display = ('id', 'order_id', 'catalog_id', 'quantity')
    list_filter = ('order_id', 'catalog_id')
    search_fields = ('catalog_id',)

    def get_queryset(self, request):
        """
        Return a QuerySet of model instances that can be edited by the admin site.
        """

        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(order_id__order_status='saved', catalog_id__provider_id__user=request.user)

    def has_add_permission(self, request):
        """
        Return False since addition of new OrderItem instances is not allowed by the admin site.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Return False since delete of OrderItem instances is not allowed by the admin site.
        """
        return False


class ImportCatalogItems(CustomModelPage):
    """
    Construct admin page for stock import operation based on user URL input.
    """
    title = 'Import catalog items'

    url = models.CharField('url', max_length=500)

    def save(self):
        """
        Implementation of URL input form save handling. Calls celery task for catalog
        items import and returns task_id to user
        so user could check the execution of import operations via separate route.
        """
        res = do_import.delay(self.url)

        self.bound_admin.message_warning(self.bound_request, f'Import started. Task id to get result - {res.task_id}')


ImportCatalogItems.register()
