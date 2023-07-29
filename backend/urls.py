from django.urls import path

from backend.views import ShopUpdate

app_name = 'backend'
urlpatterns = [
    path('update', ShopUpdate.as_view(), name='shop-update'),
]
