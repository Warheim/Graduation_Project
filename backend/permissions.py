from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """
    Permission class to grant permissions to user whose type is 'customer'
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        return request.user.type == 'customer'

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.type == 'customer'


class IsProvider(BasePermission):
    """
    Permission class to grant permissions to user whose type is 'provider'
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        return request.user.type == 'provider'

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.type == 'provider'


class IsAdmin(BasePermission):
    """
    Permission class to grant permissions to user whose 'is_superuser' status is True
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user.is_superuser


class IsUser(BasePermission):
    """
    Permission class to grant permissions on user instances
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj


class IsOwner(BasePermission):
    """
    Permission class to grant permissions on instances referred to user
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.user


class IsCatalogOwner(BasePermission):
    """
    Permission class to grant permissions on catalog instances to user owning their provider instance
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == 'provider':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.customer.user


class IsCatalogReferencedOwner(BasePermission):
    """
    Permission class to grant permissions on catalog referring instances to user owning this catalog customer instance
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == 'provider':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.catalog.provider_id.user


class IsCustomerOwner(BasePermission):
    """
    Permission class to grant permissions on instances to user owning their purchaser instance
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == 'customer':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.customer.user


class IsOrderOwner(BasePermission):
    """
    Permission class to grant permissions on order to provider, which is owner of at least one position from order
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == "provider":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        for position in obj.order_items.all():
            if position.catalog.provider_id.user == request.user:
                return True
        return False


class IsOrderItemOwner(BasePermission):
    """
    Permission class to grant permissions on order positions to customer, which is owner of order
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == 'customer':
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return request.user == obj.order.customer_id.user


class IsOrderCatalogOwner(BasePermission):
    """
    Permission class to grant permissions on order to provider, which is owner of at least one position from order
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.user.is_anonymous:
            return False
        if request.user.type == "provider":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        for position in obj.order_items.all():
            if position.catalog_id.provider_id.user == request.user:
                return True
        return False
